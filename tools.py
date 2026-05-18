"""
tools.py
────────
Defines the 4 tools the LangGraph agent can call autonomously.

WHAT ARE TOOLS IN LANGCHAIN/LANGGRAPH?
  Tools are Python functions decorated with @tool. When the LLM decides
  it needs to use one, it outputs a structured tool_call containing:
    - The tool name
    - The arguments (as a JSON-like dict)

  LangGraph's ToolNode intercepts these, executes the real Python function,
  and returns the result back into the message stream for the agent to read.

INTERVIEW TALKING POINT:
  "Function calling / tool use is how we give LLMs agency. The LLM doesn't
   execute code — it outputs structured JSON describing what it wants to do.
   My Python functions do the actual work. LangGraph orchestrates the loop:
   agent decides → tool executes → agent reads result → agent decides again."

THE 4 TOOLS:
  1. search_engineering_documents  — RAG retrieval from knowledge base
  2. calculate_engineering_metric  — Engineering calculations (Eurocode)
  3. classify_risk_level            — Risk matrix assessment
  4. generate_structured_report    — Formal report compilation
"""

import json
import math
from datetime import datetime
from langchain_core.tools import tool
from data.knowledge_base import KnowledgeBase

# Initialise knowledge base once at module load
_kb = KnowledgeBase()


# ═══════════════════════════════════════════════════════════════════════════
# TOOL 1 — DOCUMENT SEARCH (RAG)
# ═══════════════════════════════════════════════════════════════════════════

@tool
def search_engineering_documents(query: str) -> str:
    """
    Search the engineering knowledge base for relevant standards,
    guidelines, precedents, and technical documentation.

    Always call this tool FIRST before answering any technical question.
    It retrieves the most relevant documents to ground your answer in
    verified engineering standards rather than general knowledge.

    Args:
        query: A specific search query describing the information needed.
               Example: "foundation design clay soil bearing capacity"

    Returns:
        Ranked list of relevant document excerpts with source references.
    """
    results = _kb.search(query, top_k=3)

    if not results:
        return (
            "No relevant documents found in the knowledge base for this query.\n"
            "Proceeding with general engineering knowledge — flag this as an assumption."
        )

    output = f"KNOWLEDGE BASE SEARCH RESULTS ({len(results)} documents found)\n"
    output += "═" * 60 + "\n\n"

    for i, doc in enumerate(results, 1):
        output += f"[{i}] {doc['title']}\n"
        output += f"    Source:    {doc['source']}\n"
        output += f"    Relevance: {'█' * int(doc['score'] / 2)}{' ' * (10 - int(doc['score'] / 2))} ({doc['score']:.1f})\n\n"
        output += f"{doc['content']}\n"
        output += "─" * 60 + "\n\n"

    return output


# ═══════════════════════════════════════════════════════════════════════════
# TOOL 2 — ENGINEERING CALCULATIONS
# ═══════════════════════════════════════════════════════════════════════════

@tool
def calculate_engineering_metric(
    calculation_type: str,
    parameters: str
) -> str:
    """
    Perform standard engineering calculations using accepted industry formulas.

    Available calculation types:
      - "load_factor"       : Eurocode ULS load combination (EN 1990 Exp 6.10b)
      - "bearing_capacity"  : Terzaghi ultimate bearing capacity
      - "safety_factor"     : General safety factor check (R/S)
      - "carbon_footprint"  : Embodied carbon estimate (RICS WLCA)

    Args:
        calculation_type: One of the types listed above.
        parameters: JSON string of input values.
                    Example for load_factor: '{"dead_load": 50, "live_load": 30, "wind_load": 10}'

    Returns:
        Calculation result with formula, working, and result clearly shown.
    """
    # ── Parse parameters ──────────────────────────────────────────────────
    try:
        params = json.loads(parameters)
    except json.JSONDecodeError:
        return (
            f"ERROR: 'parameters' must be a valid JSON string.\n"
            f"Example: '{{\"dead_load\": 50, \"live_load\": 30}}'\n"
            f"Received: {parameters}"
        )

    # ── Dispatch to correct calculation ───────────────────────────────────
    calculators = {
        "load_factor":      _calc_load_factor,
        "bearing_capacity": _calc_bearing_capacity,
        "safety_factor":    _calc_safety_factor,
        "carbon_footprint": _calc_carbon_footprint,
    }

    if calculation_type not in calculators:
        available = "\n  - ".join(calculators.keys())
        return f"Unknown calculation type: '{calculation_type}'\nAvailable:\n  - {available}"

    return calculators[calculation_type](params)


def _calc_load_factor(p: dict) -> str:
    Gk  = p.get("dead_load",  0)   # Permanent / dead load (kN/m²)
    Qk  = p.get("live_load",  0)   # Variable / live load (kN/m²)
    Wk  = p.get("wind_load",  0)   # Wind load (kN/m²)
    xi  = p.get("xi",      0.925)  # Reduction factor ξ

    # Eurocode EN 1990 Expression 6.10b (ULS fundamental)
    uls = xi * 1.35 * Gk + 1.5 * Qk + 0.9 * Wk
    total_unfactored = Gk + Qk + Wk

    return f"""
LOAD COMBINATION CALCULATION  ·  Eurocode EN 1990 Exp. 6.10b (ULS)
{'━'*56}
INPUTS
  Dead Load  Gk  = {Gk:>8.2f} kN/m²
  Live Load  Qk  = {Qk:>8.2f} kN/m²
  Wind Load  Wk  = {Wk:>8.2f} kN/m²
  ξ factor       = {xi:>8.3f}

FORMULA
  Ed = ξ·γG·Gk + γQ·Qk + 0.9·Wk
     = {xi}×1.35×{Gk} + 1.5×{Qk} + 0.9×{Wk}

RESULT
  Design Load (ULS)    = {uls:.2f} kN/m²
  Unfactored Total     = {total_unfactored:.2f} kN/m²
  Load amplification   = {(uls/total_unfactored*100 if total_unfactored else 0):.1f}%
{'━'*56}
  ⚠  Check SLS (serviceability) separately with unfactored loads.
"""


def _calc_bearing_capacity(p: dict) -> str:
    c    = p.get("cohesion",      25)   # Undrained cohesion (kPa)
    phi  = p.get("friction_angle", 30)  # Internal friction angle (degrees)
    Df   = p.get("depth",         1.5)  # Foundation depth (m)
    B    = p.get("width",         1.0)  # Foundation width (m)
    gam  = p.get("density",       18)   # Soil unit weight (kN/m³)

    phi_r = math.radians(phi)

    # Terzaghi bearing capacity factors
    if phi > 0:
        Nq = math.exp(math.pi * math.tan(phi_r)) * (math.tan(math.radians(45 + phi/2)))**2
        Nc = (Nq - 1) / math.tan(phi_r)
        Ng = 2.0 * (Nq + 1) * math.tan(phi_r)
    else:
        Nq, Nc, Ng = 1.0, 5.14, 0.0

    q    = gam * Df          # Overburden stress at foundation level
    qu   = c*Nc + q*Nq + 0.5*gam*B*Ng  # Ultimate bearing capacity
    safe = qu / 3.0          # Safe bearing capacity (FoS = 3)

    return f"""
ULTIMATE BEARING CAPACITY  ·  Terzaghi (1943) General Formula
{'━'*56}
INPUTS
  Cohesion c           = {c:>7.1f} kPa
  Friction angle φ     = {phi:>7.1f}°
  Foundation depth Df  = {Df:>7.2f} m
  Foundation width B   = {B:>7.2f} m
  Soil unit weight γ   = {gam:>7.1f} kN/m³

BEARING CAPACITY FACTORS
  Nc = {Nc:.3f}   Nq = {Nq:.3f}   Nγ = {Ng:.3f}

FORMULA
  qu = c·Nc + q·Nq + 0.5·γ·B·Nγ
     = {c}×{Nc:.2f} + {q:.1f}×{Nq:.2f} + 0.5×{gam}×{B}×{Ng:.2f}

RESULT
  Ultimate Bearing Capacity qu = {qu:.2f} kPa
  Safe Bearing Capacity (FoS 3) = {safe:.2f} kPa
{'━'*56}
  ⚠  Verify with site investigation data. EC7 partial factors
     may differ from FoS = 3 depending on Design Approach.
"""


def _calc_safety_factor(p: dict) -> str:
    R = p.get("resistance", 0)   # Resistance / capacity
    S = p.get("load",       0)   # Applied load / demand

    if S == 0:
        return "ERROR: 'load' (demand S) cannot be zero."

    sf = R / S

    if sf >= 3.0:
        status = "✅ VERY SAFE   — Significantly over-designed, consider optimisation"
    elif sf >= 2.0:
        status = "✅ SAFE        — Comfortable margin, standard for most permanent works"
    elif sf >= 1.5:
        status = "✅ ADEQUATE    — Meets minimum requirement for structural elements"
    elif sf >= 1.0:
        status = "⚠️  MARGINAL   — Above unity but below design minimum, review required"
    else:
        status = "❌ INADEQUATE  — Below unity, structural failure possible, DO NOT USE"

    return f"""
SAFETY FACTOR CHECK
{'━'*40}
  Resistance R    = {R:.2f} kN (or kN/m²)
  Applied Load S  = {S:.2f} kN (or kN/m²)

  Safety Factor   = R ÷ S = {sf:.3f}

STATUS: {status}

  Minimum FoS benchmarks:
    Temporary works:        1.3 – 1.5
    Permanent structures:   1.5 – 2.0
    Geotechnical (slope):   1.3 (min) / 1.5 (design)
    Nuclear / critical:     3.0+
{'━'*40}
"""


def _calc_carbon_footprint(p: dict) -> str:
    concrete_m3    = p.get("concrete_m3",    0)
    steel_tonnes   = p.get("steel_tonnes",   0)
    timber_m3      = p.get("timber_m3",      0)
    transport_tkm  = p.get("transport_tkm",  0)   # tonne-kilometres

    # Embodied carbon emission factors (kgCO2e per unit) — RICS WLCA 2023
    EF_concrete   = 300    # kgCO2e/m³ (C30/37 standard)
    EF_steel      = 1_800  # kgCO2e/tonne (virgin structural steel)
    EF_timber     = -900   # kgCO2e/m³ (sequestration credit, glulam)
    EF_transport  = 0.15   # kgCO2e/tonne-km (HGV road)

    co2_concrete  = concrete_m3   * EF_concrete
    co2_steel     = steel_tonnes  * EF_steel
    co2_timber    = timber_m3     * EF_timber
    co2_transport = transport_tkm * EF_transport
    total         = co2_concrete + co2_steel + co2_timber + co2_transport

    return f"""
EMBODIED CARBON ESTIMATE  ·  RICS Whole Life Carbon Assessment 2023
{'━'*56}
MATERIAL CARBON
  Concrete  {concrete_m3:>6} m³   × {EF_concrete} kgCO2e/m³   = {co2_concrete:>10,.0f} kgCO2e
  Steel     {steel_tonnes:>6} t    × {EF_steel} kgCO2e/t    = {co2_steel:>10,.0f} kgCO2e
  Timber    {timber_m3:>6} m³   × {EF_timber} kgCO2e/m³  = {co2_timber:>10,.0f} kgCO2e
  Transport {transport_tkm:>6} t·km × {EF_transport} kgCO2e/t·km = {co2_transport:>10,.0f} kgCO2e
{'─'*56}
  TOTAL EMBODIED CARBON                          {total:>10,.0f} kgCO2e
                                                 {total/1000:>10.1f} tCO2e
{'━'*56}
  RICS benchmark (commercial, per m² GIA): 600–900 kgCO2e/m²
  Reduction targets: LETI 2030 = 300 kgCO2e/m²
  ⚠  Use project-specific EPDs where available for accuracy.
"""


# ═══════════════════════════════════════════════════════════════════════════
# TOOL 3 — RISK CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════

@tool
def classify_risk_level(
    risk_description: str,
    likelihood: str,
    consequence: str
) -> str:
    """
    Classify a project risk using a standard 5×5 engineering risk matrix.

    The risk score (likelihood × consequence) determines the risk level
    and triggers appropriate required actions and mitigations.

    Args:
        risk_description: Clear, specific description of the risk event.
                          Example: "Ground collapse during excavation adjacent to live railway"
        likelihood:       One of: rare | unlikely | possible | likely | almost_certain
        consequence:      One of: negligible | minor | moderate | major | catastrophic

    Returns:
        Risk classification with score, level, required actions, and mitigations.
    """
    likelihood_map = {
        "rare":            (1, "<5% probability, exceptional circumstances only"),
        "unlikely":        (2, "5–25% probability, could occur at some time"),
        "possible":        (3, "25–50% probability, might occur at some time"),
        "likely":          (4, "50–85% probability, will probably occur"),
        "almost_certain":  (5, ">85% probability, expected to occur"),
    }
    consequence_map = {
        "negligible":     (1, "No injury, negligible cost/programme impact"),
        "minor":          (2, "First aid injury, minor cost/programme impact"),
        "moderate":       (3, "Medical treatment, significant cost/programme impact"),
        "major":          (4, "Serious injury / significant environmental damage"),
        "catastrophic":   (5, "Fatality / total project failure / irreversible damage"),
    }

    l_key = likelihood.lower().replace(" ", "_")
    c_key = consequence.lower().replace(" ", "_")

    if l_key not in likelihood_map:
        return f"Invalid likelihood '{likelihood}'. Options: {', '.join(likelihood_map.keys())}"
    if c_key not in consequence_map:
        return f"Invalid consequence '{consequence}'. Options: {', '.join(consequence_map.keys())}"

    l_score, l_desc = likelihood_map[l_key]
    c_score, c_desc = consequence_map[c_key]
    risk_score = l_score * c_score

    # Risk level determination
    if risk_score >= 15:
        level, colour, action = "CRITICAL", "🔴", "STOP work. Immediate escalation to Project Director. Do not proceed without written approval."
    elif risk_score >= 10:
        level, colour, action = "HIGH",     "🟠", "Senior management attention required. Detailed mitigation plan and specialist review needed."
    elif risk_score >= 6:
        level, colour, action = "MEDIUM",   "🟡", "Management responsibility. Implement specific mitigation measures and monitor."
    elif risk_score >= 3:
        level, colour, action = "LOW",      "🟢", "Manage by routine procedures. Document and monitor."
    else:
        level, colour, action = "VERY LOW", "🟢", "Accept with standard monitoring. Log in risk register."

    mitigations = {
        "CRITICAL": [
            "Halt works and initiate emergency review",
            "Appoint specialist consultant for independent assessment",
            "Notify relevant regulatory/statutory body",
            "Issue formal risk notification to client",
            "Full redesign or alternative methodology review",
        ],
        "HIGH": [
            "Implement engineering controls before works proceed",
            "Increase inspection frequency to daily minimum",
            "Senior / chartered engineer sign-off required",
            "Real-time monitoring system deployment",
            "Update project risk register and client RAMS",
        ],
        "MEDIUM": [
            "Specific mitigation measures to be implemented",
            "Weekly monitoring and review",
            "Document in project risk register",
            "Team awareness briefing and toolbox talk",
        ],
        "LOW": [
            "Standard site management procedures apply",
            "Include in site induction briefing",
            "Monitor at routine intervals",
        ],
        "VERY LOW": [
            "Accept with standard monitoring",
            "Log in risk register for completeness",
        ],
    }

    mit_list = "\n".join(f"  {i+1}. {m}" for i, m in enumerate(mitigations[level]))

    return f"""
RISK ASSESSMENT  ·  5×5 Risk Matrix
{'━'*56}
RISK:         {risk_description}
{'─'*56}
LIKELIHOOD:   {likelihood.title()} ({l_score}/5)
              {l_desc}

CONSEQUENCE:  {consequence.title()} ({c_score}/5)
              {c_desc}
{'─'*56}
RISK SCORE:   {l_score} × {c_score} = {risk_score}/25

RISK LEVEL:   {colour}  {level}
{'─'*56}
REQUIRED ACTION:
  {action}

RECOMMENDED MITIGATIONS:
{mit_list}
{'━'*56}
  Record in project risk register with owner and target date.
"""


# ═══════════════════════════════════════════════════════════════════════════
# TOOL 4 — REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

@tool
def generate_structured_report(
    project_name: str,
    query_addressed: str,
    findings: str,
    recommendations: str,
    standards_cited: str = "See findings above"
) -> str:
    """
    Compile all findings into a professional engineering report.

    Call this tool LAST, after searching documents and conducting any
    calculations or risk assessments needed to fully answer the query.

    Args:
        project_name:     Name of the project or assessment being reported on.
        query_addressed:  The original engineering question this report answers.
        findings:         Key technical findings from documents, calculations, and risk assessments.
        recommendations:  Actionable next steps and engineering recommendations.
        standards_cited:  List of standards and references used (optional).

    Returns:
        Formatted engineering report ready for engineer review.
    """
    timestamp = datetime.now().strftime("%d %B %Y — %H:%M UTC")
    border = "═" * 62

    report = f"""
{border}
 ENGINEERING INTELLIGENCE REPORT
  AI Accelerator — Prototype v1.0
{border}

  PROJECT   :  {project_name}
  DATE      :  {timestamp}
  PREPARED  :  Engineering AI Agent (Azure OpenAI GPT-4o)
  STATUS    :  DRAFT — Requires qualified engineer review before use

{border}
  QUERY ADDRESSED
{'─'*62}
  {query_addressed}

{border}
  TECHNICAL FINDINGS
{'─'*62}
{findings}

{border}
  STANDARDS & REFERENCES CITED
{'─'*62}
  {standards_cited}

{border}
  RECOMMENDATIONS
{'─'*62}
{recommendations}

{border}
  DISCLAIMER
{'─'*62}
  This report was generated by an AI agent and MUST be reviewed
  and validated by a qualified engineer before use in any
  professional, contractual, or regulatory capacity.

  AI-generated content may contain errors or omissions.
  Engineer's professional judgement supersedes this output.

{'─'*62}
  Generated by: Engineering Intelligence Agent
  Powered by: Azure OpenAI GPT-4o + LangGraph + Python
  Repository: github.com/H420UN/engineering-intelligence-agent
{border}
"""
    return report

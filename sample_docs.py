"""
sample_docs.py
──────────────
Sample engineering documents that populate the knowledge base.
In a real WSP deployment, these would be replaced with:
  - Internal project precedents
  - Company design standards
  - Indexed versions of BS/Eurocode documents
  - Client-specific technical specifications

INTERVIEW TALKING POINT:
  "In production, this layer would be replaced with Azure AI Search
   using vector embeddings from Azure OpenAI text-embedding-3-large.
   Documents would be chunked, embedded, and indexed so semantic
   search retrieves by meaning, not just keywords."
"""

SAMPLE_DOCUMENTS = [
    {
        "id": "DOC-001",
        "title": "Foundation Design on Clay Soils — BS EN 1997 (Eurocode 7)",
        "source": "WSP Internal Design Standard DS-GEO-001",
        "category": "geotechnical",
        "content": """
Foundation design on clay soils must comply with BS EN 1997-1:2004 (Eurocode 7).
Key considerations for clay foundations:

BEARING CAPACITY:
- Undrained shear strength (Cu) must be determined from site investigation data
- Minimum 3 boreholes for sites under 0.5 hectares; 1 per 0.25ha thereafter
- Net ultimate bearing capacity: qnet = Nc × Cu (Nc = 9 for deep foundations)
- Apply partial factor γcu = 1.4 for derived Cu values (Design Approach 1)

SETTLEMENT:
- Consolidation settlement in clay is time-dependent and must be modelled
- Primary consolidation using Terzaghi one-dimensional consolidation theory
- Secondary compression (creep) significant for soft clays and organic soils
- Acceptable total settlement: typically 25mm for isolated foundations
- Differential settlement limit: span/500 or 20mm, whichever is less

FOUNDATION TYPES BY SOIL CONDITION:
- Stiff clay (Cu > 75 kPa): Strip or pad foundations typically adequate
- Firm clay (Cu 40–75 kPa): Raft or piled foundation recommended
- Soft clay (Cu < 40 kPa): Piled foundation to competent stratum required
- Shrinkable clay: Minimum foundation depth 0.9m; 1.5m near trees (NHBC CH4)

WATER TABLE:
- If WT within 0.5m of foundation level, buoyancy uplift must be checked
- Heave potential in over-consolidated clay must be assessed
""",
        "keywords": ["foundation", "clay", "soil", "bearing", "settlement", "eurocode", "geotechnical", "pile", "raft"]
    },
    {
        "id": "DOC-002",
        "title": "Environmental Impact Assessment — Infrastructure Projects",
        "source": "WSP Environmental Practice Note EPN-003",
        "category": "environmental",
        "content": """
Environmental Impact Assessment (EIA) requirements for infrastructure projects
in the UK are governed by the Town and Country Planning (EIA) Regulations 2017.

SCREENING CRITERIA (Schedule 2 developments requiring EIA):
- Projects in sensitive areas (SSSIs, AONBs, Green Belt, flood zones)
- Projects exceeding EIA thresholds (e.g. >150,000m² floor space, >10ha area)
- Projects likely to have significant effects on the environment

WETLAND IMPACTS — SPECIFIC GUIDANCE:
- Projects within 500m of a designated wetland require Habitats Regulations 
  Assessment (HRA) under the Conservation of Habitats Regulations 2017
- Hydrological connectivity assessment is mandatory
- Water quality baseline monitoring: minimum 12 months pre-construction
- Protected species survey: great crested newts, water voles, otters (mandatory)
- Mitigation hierarchy must be applied: Avoid → Mitigate → Compensate
- BREEAM Excellent or LEED Gold minimum for buildings within 1km of SSSI

ECOLOGICAL IMPACT ASSESSMENT:
- Phase 1 Habitat Survey required for all development sites
- Phase 2 surveys triggered by Phase 1 findings or statutory designations
- Biodiversity Net Gain (BNG): 10% mandatory gain from Nov 2023 (TCPA 2008 s40A)
- Net gain calculated using DEFRA Biodiversity Metric 4.0

FLOOD RISK:
- Sequential test required for all development in flood zones 2 and 3
- Exception test required for essential infrastructure in zone 3b
- Finished floor levels: minimum 300mm above 1-in-100-year flood level + climate change
""",
        "keywords": ["environment", "EIA", "wetland", "ecological", "flood", "biodiversity", "habitat", "assessment", "SSSI"]
    },
    {
        "id": "DOC-003",
        "title": "Structural Load Factors — Bridges and Footbridges",
        "source": "WSP Structural Design Guidance SDG-BRIDGE-002",
        "category": "structural",
        "content": """
Structural load factors for bridge and footbridge design per BS EN 1990 and BS EN 1991.

PEDESTRIAN BRIDGES — CHARACTERISTIC LOADS:
- Uniformly Distributed Load (UDL): 5.0 kN/m² (BS EN 1991-2 NA)
- Concentrated load: 10 kN on 100mm × 100mm footprint (maintenance check)
- Horizontal load: 10% of vertical UDL applied simultaneously at deck level
- Dynamic factor: Resonance check required if natural frequency < 5 Hz (vertical)
  or < 2.5 Hz (lateral) — refer to HiVoSS guidelines

LOAD COMBINATIONS (ULS — Fundamental):
- Expression 6.10b (EC0): ξ×γG×Gk + γQ×Qk + Σγψ0×Qk,i
  - γG = 1.35 (permanent), γQ = 1.5 (variable), ξ = 0.925
- For bridges: STR/GEO limit states must both be checked

HIGHWAY BRIDGES — TRAFFIC LOADS:
- Load Model 1 (LM1): Tandem system + UDL (primary models)
- Load Model 2 (LM2): Single axle for local verification
- Fatigue loading: Load Model 3 or 4 for steel and concrete fatigue checks
- Accidental loading: vehicle impact on supports per EN 1991-1-7 Table 4.1

MATERIALS PARTIAL FACTORS (ULS):
- Concrete: γc = 1.5 (persistent/transient), 1.2 (accidental)
- Steel reinforcement: γs = 1.15
- Structural steel: γM0 = 1.0, γM1 = 1.0, γM2 = 1.25 (fracture)

SERVICEABILITY (SLS):
- Deflection limit: span/360 under imposed load (typical)
- Crack width: wk ≤ 0.3mm (XC2-XC4 exposure), 0.2mm (XS/XD exposure)
- Vibration: acceleration limit 0.7 m/s² vertical (EN 1990 A2.4.3.2)
""",
        "keywords": ["bridge", "footbridge", "load", "structural", "pedestrian", "eurocode", "UDL", "traffic", "deflection"]
    },
    {
        "id": "DOC-004",
        "title": "Tunnelling in Urban Environments — Risk Framework",
        "source": "WSP Tunnelling Practice Note TPN-001 / CIRIA C671",
        "category": "tunnelling",
        "content": """
Urban tunnelling risk framework based on CIRIA C671 and ITA guidelines.

GROUND MOVEMENT RISKS:
- Volume loss target: ≤ 0.5% (TBM in stiff clay); 1-2% (NATM)
- Settlement trough: Gaussian distribution, i = K × z0 (K=0.5 for clay)
- Building damage assessment using Burland classification:
  Category 0-1: negligible to very slight (cosmetic only)
  Category 2: slight (minor cracking, threshold for monitoring)
  Category 3-4: moderate to severe (structural intervention required)
  Category 5: very severe (demolition may be required)

PRE-CONSTRUCTION REQUIREMENTS:
- Building condition surveys: all structures within 2× tunnel diameter + 10m
- Real-time settlement monitoring: optical targets, inclinometers, prisms
- Alert/Action/Alarm thresholds set at 50%/75%/100% of design limits
- Utility mapping to PAS 128 Level B minimum (SUE investigation)

GROUNDWATER MANAGEMENT:
- Dewatering risk: drawdown radius calculated using Sichardt's formula
- Licensed abstraction may be required under Water Resources Act 1991
- Contamination pathway assessment: Phase 1 and Phase 2 ESA
- Piezometric monitoring during and post-construction (12 months minimum)

STRUCTURAL PROTECTION MEASURES:
- Grouting/compensation grouting for sensitive structures
- Temporary propping and underpinning for Category 2+ buildings
- Vibration limits: BS 7385-2:1993 (cosmetic damage), HS2 Contractor Requirements
""",
        "keywords": ["tunnel", "tunnelling", "urban", "settlement", "ground movement", "TBM", "monitoring", "risk", "building damage"]
    },
    {
        "id": "DOC-005",
        "title": "Site Safety & Risk Assessment — Construction Phase",
        "source": "WSP Health, Safety & Wellbeing Standard HSW-CON-001",
        "category": "safety",
        "content": """
Construction phase health and safety requirements under CDM Regulations 2015.

PRINCIPAL DESIGNER DUTIES:
- Pre-construction health and safety file compilation
- Design risk assessment: eliminate hazards at design stage where possible
- Residual risk register maintained and transferred to Principal Contractor
- Structural temporary works considerations highlighted in design

SITE-SPECIFIC RISK FACTORS:
HIGH RISK activities requiring specific method statements and RAMS:
  1. Excavation >1.2m depth adjacent to structures or roads
  2. Work at height >2m sustained duration
  3. Confined space entry (oxygen deficient or toxic atmosphere potential)
  4. Demolition of structures with asbestos, lead paint, or unknown materials
  5. Temporary works with imposed loads >5 kN/m²
  6. Ground-bearing works on contaminated land

MONITORING AND REVIEW:
- Daily toolbox talks mandatory for high-risk activities
- Weekly site safety inspections: recorded and signed off by site manager
- Incident reporting: RIDDOR reportable incidents within 10 days (fatal: immediate)
- Near-miss reporting culture: tracked KPI — target >20 near misses per 100,000 hours

ENVIRONMENTAL CONTROLS:
- Noise monitoring: BS 5228 compliance during working hours
- Dust suppression: IAQM Low Emission Strategy where required
- Concrete washout: contained and licensed for disposal
- Fuel/chemical storage: bunded, minimum 110% capacity
""",
        "keywords": ["safety", "CDM", "risk", "site", "construction", "RAMS", "health", "excavation", "confined space"]
    },
    {
        "id": "DOC-006",
        "title": "Net Zero Carbon — Whole Life Carbon Assessment",
        "source": "WSP Net Zero Carbon Framework NZCF-001 / RICS Whole Life Carbon Assessment",
        "category": "sustainability",
        "content": """
Whole Life Carbon (WLC) assessment methodology per RICS Professional Standard 2023
and aligned to UK Green Building Council's Net Zero Carbon Buildings Framework.

CARBON ASSESSMENT BOUNDARIES:
Upfront Carbon (A1-A5):
  - A1-A3: Product stage (raw material extraction, transport to manufacturer, manufacturing)
  - A4: Transport to site
  - A5: Construction installation process

In-Use Carbon (B1-B7):
  - B4: Replacement of components
  - B6: Operational energy (regulated and unregulated)
  - B7: Operational water

End of Life (C1-C4):
  - Deconstruction, transport, waste processing, disposal

EMBODIED CARBON BENCHMARKS (kgCO2e/m² GIA):
  - Low-rise residential: 400-600 kgCO2e/m²
  - Commercial office: 600-900 kgCO2e/m²
  - Infrastructure (road per km): 200-2,000 tCO2e/km (varies significantly)

KEY REDUCTION STRATEGIES:
1. Low-carbon concrete: GGBS/PFA cement replacement (up to 70% reduction in A1-A3)
2. Structural efficiency: optimise section sizes; avoid over-engineering
3. Reuse/reclaim: recycled steel has 75% lower embodied carbon vs. virgin
4. Timber/mass timber: carbon sequestration credit under EN 16485
5. Modular/offsite manufacture: reduced waste and improved quality

REPORTING REQUIREMENTS:
- LETI Climate Emergency Design Guide targets
- GLA Circular Economy Statement for major London developments
- RIBA 2030 Climate Challenge benchmarks for net zero alignment
""",
        "keywords": ["carbon", "net zero", "sustainability", "embodied carbon", "whole life", "RICS", "concrete", "steel", "emissions"]
    }
]

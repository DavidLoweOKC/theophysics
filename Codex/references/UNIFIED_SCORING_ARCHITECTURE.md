# UNIFIED SCORING ARCHITECTURE v1.0
## Theophysics Paper Evaluation System

**Author:** David Lowe & Claude (Opus)  
**Date:** 2026-02-15  
**Status:** Implementation Specification  
**Location:** `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\`

---

## 1. SYSTEM MAP

Three scoring engines exist. Each measures something different. All three are needed.

### System 1: Writing Quality (`vault_metrics.py` + `vault_scorer.py`)

**Question it answers:** Is this paper ready to publish?

**Method:** 37 surface metrics — word count, type-token ratio, sentence complexity, graph metrics. Statistical measurement of prose quality. No interpretation of content.

**Output:** 0–100 master score + 10 domain breakdowns (Logical Coherence, Structural Integrity, Concept Density, etc.)

**Strengths:** Keyword/statistical approaches work fine for surface quality. Fast. Deterministic. No API calls.

**Weaknesses:** Cannot tell you whether a well-written paper says anything true.

**Status:** Operational. No changes needed.

---

### System 2: Theoretical Coherence (`unified_scorer.py`)

**Question it answers:** Is this theory worth publishing?

**Method:** χ/κ/ρ scoring with 12 Fruits of the Spirit, 9 structural constraints, defense layer (UTDGS), 10 Master Equation variables mapped to Triad (Π/A/Λ).

**Output:** χ (0–10 coherence), κ (0–1 confidence), ρ (0–1 robustness). Veto gates on constraint violations.

**Strengths:** The architecture is right — measuring structural properties of theories through 12 independent dimensions mapped to physical variables. The Triad decomposition (Polis/Anthropos/Logos) is genuinely novel.

**Weaknesses — CRITICAL:**

1. **Fruit detection is keyword-based.** The `fruit_matrix.yaml` file maps each Fruit to a list of words. Love = scan for "love, compassion, care, empathy." A 4,400-word physics paper about quantum decoherence in Genesis contains none of those words. Six Fruits return exactly 0.00. The detector is blind, not the paper.

2. **No section boundary parsing.** The scorer treats the entire document as a single block. When a paper includes a 700-line self-critique section (as the Genesis papers do), words like "false," "contradiction," "misapplied," and "error" in the critique section are scored as if the theory itself contains those flaws. This causes Non-Contradiction vetoes on papers that are internally consistent. Three papers capped at χ=3.0 because of this contamination.

3. **Triad components center at 0.5.** Formula: `value = 0.5 + (fruit.net * weight * 0.5)`. When fruit.net ≈ 0 (because the detector found nothing), all Triad scores hover at 0.49–0.55. This is an artifact of blind detection, not a real measurement.

**Status:** Architecture sound. Detection layer needs rebuild. This document specifies the fix.

---

### System 3: Theory Comparison (`theophysics_compare.py`)

**Question it answers:** How does this theory compare to a baseline?

**Method:** Epistemic Drift Bands (EDB) per domain + invariant proxy scoring + pairwise cosine similarity. Ingests entire theory folders. Compares candidate theories against a baseline.

**Output:** Similarity score (0–1), ranked comparisons, per-domain EDB profiles, full audit trail with SHA-256 hashes and config snapshots.

**Strengths:**

- **Honest about its limits.** Comments say "proxies, not direct measures." The `coherence_proxy` checks for definition sections, scope statements, falsifiability markers, equations, citations — structural signals a coherent theory *tends to have*. Legitimate proxy measurement.
- **Epistemic Drift Bands.** Each domain gets a 5-axis tolerance profile. Physics = (5,5,1,5,5) — high rigor, low interpretive latitude. Theology = (2,1,4,2,1) — low rigor expectations, high interpretive latitude. A theology paper scoring low on falsifiability markers isn't penalized the same as a physics paper. This handles multi-domain papers like the Genesis series.
- **Auditable by design.** Every score has a trace. Config snapshots included. Deterministic — same input produces same output.

**Weaknesses:** Domain detection is keyword-based (same shallow problem). `virtue_language_proxy` scans for "love," "grace," "truth" as words — same trap as `fruit_matrix.yaml`.

**Status:** Operational for comparison purposes. EDB framework should be adopted into System 2.

---

## 2. INTEGRATION ARCHITECTURE

### How the Three Systems Feed Each Other

```
PAPER IN
    │
    ▼
┌──────────────────────────────────────────┐
│  SECTION BOUNDARY PARSER (new)           │
│  Splits: Theory | Critique | Appendix    │
│  Tags each section with type             │
└──────────────┬───────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│System 1│ │System 2│ │System 3│
│Writing │ │Theory  │ │Compare │
│Quality │ │Cohere. │ │Baseline│
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    ▼          ▼          ▼
┌──────────────────────────────────────────┐
│  MASTER SCORE MATRIX                      │
│                                           │
│  Paper    WQ   χ    κ    ρ    Sim   EDB  │
│  GEN-001  72   6.8  0.71 0.85 0.82  ...  │
│  GEN-002  68   5.9  0.65 0.78 0.79  ...  │
│                                           │
│  Quadrant:                                │
│  High WQ + High χ = PUBLISH FIRST         │
│  High χ + Low WQ  = NEEDS POLISH          │
│  High WQ + Low χ  = DANGEROUS (feels      │
│                      done but isn't)       │
│  Low both          = REWORK               │
└──────────────────────────────────────────┘
```

### Decision Matrix

| Writing Quality | Theoretical Coherence | Action |
|---|---|---|
| High (>75) | High (χ > 6.5) | Publish first. Final proofread only. |
| Low (<60) | High (χ > 6.5) | Polish prose. Theory is sound. |
| High (>75) | Low (χ < 5.0) | **Dangerous.** Reads well, argues poorly. Structural rewrite. |
| Low (<60) | Low (χ < 5.0) | Full rework. Consider whether argument survives /PROBE. |

---

## 3. SECTION BOUNDARY PARSER

### Problem

The scorer treats the entire markdown file as one text block. Self-critique sections, appendices, and meta-commentary get scored as if they are part of the theory's claims.

### Detection Rules

Parse the document into scored and excluded zones:

**SCORED ZONES** (theory content):
- Everything from document start until first exclusion marker
- Sections under headings: Abstract, Introduction, Theory, Framework, Method, Results, Discussion, Conclusion, Implications, Predictions, Falsification

**EXCLUDED ZONES** (not theory claims):
- Sections under headings containing: Critique, Objection, Response, Rebuttal, Appendix, Notes, Acknowledgment, Changelog, Meta, Commentary, "What I got wrong," "AI feedback," "Things to fix"
- Block quotes that are clearly external critique (heuristic: contains "the author" or "this paper" as critique subject)
- Lines starting with `>` followed by critique language ("however," "the problem with," "this fails to")

**TAGGED BUT SCORED DIFFERENTLY:**
- Defense sections (where the author responds to objections): Score for defense strength, not as primary claims. Feed to defense layer in System 2.
- Evidence appendices (raw data, tables): Score for evidence density, not for coherence proxies.

### Implementation

```python
EXCLUSION_PATTERNS = [
    r'(?mi)^#{1,4}\s*(critique|objection|rebuttal|appendix|notes|'
    r'acknowledgment|changelog|meta|commentary|what\s+i\s+got\s+wrong|'
    r'ai\s+feedback|things\s+to\s+fix)',
]

DEFENSE_PATTERNS = [
    r'(?mi)^#{1,4}\s*(response|defense|counter|rebuttal|addressing)',
]

def split_document(text: str) -> dict:
    """Returns {'theory': str, 'critique': str, 'defense': str, 'appendix': str}"""
    # Split on markdown headers, classify each section,
    # concatenate by zone type
    ...
```

### Expected Impact

Re-scoring the Genesis papers with section boundaries:

| Paper | Current χ | Expected χ | Reason |
|---|---|---|---|
| Genesis as Quantum Event | 3.0 (veto) | 6.0–7.0 | No internal contradictions in theory itself |
| Time as Weapon V1 | 3.0 (veto) | 5.5–6.5 | Critique section was contaminating |
| Time as Weapon V2 | 5.16 | 5.5–6.0 | Already cleaner, minor improvement |
| How This Works | 5.18 | 5.5–6.0 | Meta-document, less affected |

---

## 4. THE 12 FRUIT RUBRICS — STRUCTURAL REBUILD

### The Problem

Current `fruit_matrix.yaml` maps each Fruit to a keyword list:

```yaml
F1_love:
  detection_keywords:
    positive: [love, compassion, care, empathy, kindness]
    negative: [hate, hatred, malice, cruelty, spite]
```

A physics paper about quantum decoherence doesn't contain "compassion." Score: 0.00. But the paper may exhibit Love structurally — by constructing frameworks that serve human understanding, by building bridges between hostile disciplines, by treating opposing views with intellectual charity.

The Fruits are not topics. They are structural properties of well-formed theories. The rubrics below define what each Fruit *means* when measured in a theoretical document.

### Rubric Design Principles

Each Fruit rubric specifies:

1. **Structural Definition** — What this property means in a theory, independent of domain
2. **Positive Indicators** — Observable document features that indicate presence (NOT keywords — patterns, structures, relationships)
3. **Negative Indicators** — Observable features that indicate absence or violation
4. **Measurement Method** — How to detect this using document analysis (regex where appropriate, structural analysis where needed)
5. **Scoring Range** — [-1.0, +1.0] where 0.0 means "insufficient evidence to score"
6. **GPT Academic Rule Mapping** — Which writing rules from the academic standards correspond to this Fruit

---

### F1: LOVE (Agape) — Integration Under Service

**Structural Definition:** The theory builds bridges between domains, disciplines, or perspectives for the purpose of unifying understanding. It serves the reader rather than the author. It constructs frameworks others can use, not just arguments others must accept.

**Positive Indicators:**
- Cross-domain mappings that preserve structure in both domains (not just metaphors — actual isomorphisms with constrained predictions)
- Explicit statements of what the framework offers to other fields
- Variable substitution tables showing physical → spiritual mappings that preserve symmetry
- Definitions that respect the home discipline's terminology while extending it
- Sections addressing "how others can use this"

**Negative Indicators:**
- Framework claims universality but only operates in one domain
- Author treats competing frameworks with contempt rather than structural engagement
- No attempt to connect to existing literature or parallel work
- Theory is self-contained island — no on-ramps for outsiders

**Measurement Method:**
- Count cross-domain mapping tables/sections
- Detect structural isomorphism claims (A maps to B preserving symmetry C)
- Check for explicit reader-service language vs. pure assertion
- Count variable substitution instances where both sides are defined

**GPT Rule Mapping:** "Build genuine cross-domain bridges, not surface analogies." "Each mapping must constrain predictions in both domains."

**Score Anchors:**
- +1.0: Multiple working isomorphisms with explicit symmetry preservation, reader pathways, engagement with parallel work
- +0.5: Some cross-domain work, but mappings are suggestive rather than constrained
- 0.0: Cannot determine (insufficient evidence)
- -0.5: Claims universality but operates in single domain
- -1.0: Actively hostile to adjacent frameworks, no bridges, no reader service

---

### F2: JOY (Chara) — Generative Capacity

**Structural Definition:** The theory generates more than it consumes. It opens questions, produces predictions, creates new research directions. A joyful theory makes you want to do more work, not less.

**Positive Indicators:**
- Explicit predictions that can be tested
- "This implies..." or "This predicts..." statements that go beyond the initial argument
- Open questions acknowledged as productive (not as failures)
- Framework generates applications the author didn't fully explore
- Falsification criteria that would be interesting even if they killed the theory

**Negative Indicators:**
- Theory is purely defensive (only responds to objections, generates nothing)
- No predictions, no implications, no "what follows from this"
- Falsification criteria are trivial or unfalsifiable
- Theory explains everything and predicts nothing

**Measurement Method:**
- Count prediction statements
- Count open questions framed as productive
- Check for implication sections
- Measure ratio of generative claims to defensive claims
- Detect falsification criteria and assess specificity

**GPT Rule Mapping:** "A theory that generates no testable predictions is theology, not physics." "Good falsification criteria are interesting even if they destroy the theory."

**Score Anchors:**
- +1.0: Multiple specific testable predictions, rich implications section, productive open questions, interesting falsification criteria
- +0.5: Some predictions but vague; implications mentioned but not developed
- 0.0: Cannot determine
- -0.5: Purely defensive; explains but doesn't predict
- -1.0: Actively unfalsifiable; claims to explain everything

---

### F3: PEACE (Eirene) — Internal Non-Contradiction

**Structural Definition:** The theory does not contradict itself. Its premises lead to its conclusions without logical breaks. Different sections of the paper are consistent with each other. Definitions used in Section 2 are the same definitions operating in Section 5.

**Positive Indicators:**
- Consistent use of defined terms throughout
- Conclusions that follow from stated premises
- No section contradicts another section
- Mathematical operations preserve the identities established earlier
- Variable meanings don't shift mid-argument

**Negative Indicators:**
- Term used with different meanings in different sections
- Conclusion claims something the premises don't support
- Mathematical step introduces quantity not established
- Section A asserts X, Section B assumes not-X
- Scope claimed in introduction differs from scope demonstrated

**Measurement Method:**
- **Term consistency check:** Extract defined terms → verify same definition operates throughout
- **Premise-conclusion trace:** Identify stated premises → check if conclusion follows
- **Variable stability:** Track variable names through equations → flag meaning shifts
- **Scope consistency:** Compare introduction claims to body delivery

**GPT Rule Mapping:** "State premises explicitly." "Separate structure from interpretation." "If you claim X in the abstract, deliver X in the body."

**Score Anchors:**
- +1.0: Perfect term consistency, premises demonstrably lead to conclusions, no scope drift
- +0.5: Minor term inconsistencies, conclusions mostly follow, small scope drift
- 0.0: Cannot determine
- -0.5: Significant term drift, conclusions partially unsupported, scope mismatch
- -1.0: Internal contradictions, conclusions contradict premises, fundamental inconsistency

**CRITICAL NOTE:** This Fruit is what the Non-Contradiction constraint in System 2 should measure. The current implementation detects the word "contradiction" — which triggers false positives when a critique section discusses contradictions the theory might have. The section boundary parser (§3) must run BEFORE this Fruit is scored.

---

### F4: PATIENCE (Makrothymia) — Thoroughness of Development

**Structural Definition:** The theory develops its arguments fully rather than rushing to conclusions. Each claim is given the space it needs. Intermediate steps are shown, not skipped. The author doesn't assume the reader already agrees.

**Positive Indicators:**
- Multi-step derivations with each step justified
- "First... then... therefore..." logical progression
- Intermediate results stated before combining into final claims
- Assumptions made explicit before they're used
- Worked examples that show the framework operating (not just asserting it works)

**Negative Indicators:**
- Leaps from premise to conclusion without intermediate steps
- "It is obvious that..." or "clearly..." without demonstration
- Complex claims asserted without derivation
- Reader expected to accept framework before seeing it work
- Hand-waving where rigor is needed

**Measurement Method:**
- Count logical connectives in derivation chains (therefore, thus, hence, it follows)
- Measure ratio of asserted claims to derived claims
- Detect "obvious" / "clearly" / "trivially" hedges that skip work
- Check for worked examples
- Measure derivation depth (how many intermediate steps between premise and conclusion)

**GPT Rule Mapping:** "Show your work." "Don't overclaim validation." "Every assertion needs either derivation or explicit acknowledgment that it's assumed."

**Score Anchors:**
- +1.0: Full derivation chains, worked examples, all assumptions explicit, no hand-waving
- +0.5: Mostly derived, some leaps acknowledged, partial worked examples
- 0.0: Cannot determine
- -0.5: Frequent assertion without derivation, skipped steps, "it is obvious"
- -1.0: Almost entirely asserted, no derivation, reader expected to accept on authority

---

### F5: KINDNESS (Chrestotes) — Intellectual Charity

**Structural Definition:** The theory engages opposing views with structural respect. It steelmans objections rather than strawmanning them. When it disagrees, it does so by addressing the strongest version of the counterargument, not the weakest.

**Positive Indicators:**
- Opposing views stated in their strongest form before being addressed
- "The best version of this objection would be..." language
- Acknowledgment of what competing frameworks get right
- Engagement with actual published objections, not imagined weak ones
- Theory explains *why* someone might reasonably disagree

**Negative Indicators:**
- Strawman characterizations of opposing views
- Dismissal without engagement ("critics simply fail to understand")
- No acknowledgment of competing frameworks' strengths
- Pejorative language about other theorists or traditions
- Objections addressed only in their weakest form

**Measurement Method:**
- Detect objection-response pairs; assess whether objections are steelmanned or strawmanned
- Check for acknowledgment of opposing frameworks' contributions
- Look for "the strongest objection" / "the best case for" language
- Detect dismissive language patterns
- Count engagement with named competing theories vs. unnamed straw positions

**GPT Rule Mapping:** "Steelman the opposition." "If you can't state the best objection to your own theory, you don't understand it."

**Score Anchors:**
- +1.0: Multiple steelmanned objections, explicit acknowledgment of competing strengths, no dismissiveness
- +0.5: Some engagement with opposition, but not always strongest form
- 0.0: Cannot determine
- -0.5: Mostly strawman engagement, occasional dismissiveness
- -1.0: Active hostility to opposition, no engagement with strongest counter-arguments

---

### F6: GOODNESS (Agathosyne) — Constructive Value

**Structural Definition:** The theory adds positive value to the knowledge landscape. It doesn't just tear down other theories — it builds something that works. The world is better for this theory existing, even if it turns out to be wrong.

**Positive Indicators:**
- Framework provides tools others can use regardless of whether they accept the full theory
- Methodology is replicable and transferable
- Intermediate results have standalone value
- Theory creates vocabulary or categories that clarify previously muddled discussions
- Even skeptics can extract useful structure from the work

**Negative Indicators:**
- Theory is purely destructive (tears down others without offering alternative)
- No transferable tools or methods
- Value is entirely contingent on accepting every premise
- Nothing survives if the central thesis is wrong
- Paper is a polemic, not a contribution

**Measurement Method:**
- Identify standalone-useful components (methods, categories, frameworks, tools)
- Check if intermediate results have value independent of final conclusion
- Detect transferable methodology
- Measure ratio of constructive claims to destructive claims
- Check for "even if X is wrong, Y still holds" hedging

**GPT Rule Mapping:** "Offer tools, not just arguments." "The best theories contribute something even to those who reject them."

**Score Anchors:**
- +1.0: Multiple standalone-useful contributions, transferable methodology, value survives thesis failure
- +0.5: Some useful components, but mostly dependent on full thesis acceptance
- 0.0: Cannot determine
- -0.5: Primarily destructive, minimal constructive contribution
- -1.0: Purely polemic, no transferable value, nothing survives if wrong

---

### F7: FAITHFULNESS (Pistis) — Definitional Rigor

**Structural Definition:** The theory defines its terms and uses them consistently. It is faithful to its own definitions. When it borrows terms from other fields, it says so explicitly and defines the borrowed meaning. Nothing is left to the reader's imagination.

**Positive Indicators:**
- Explicit definitions section or inline definitions before first use
- Variables defined with units, domains, and ranges
- Borrowed terms explicitly flagged ("we use X in the sense of...")
- Consistent usage throughout — same word never means two things
- Mathematical symbols defined at first appearance

**Negative Indicators:**
- Key terms used without definition
- Same term shifts meaning across sections
- Variables appear in equations without prior definition
- Technical terms from other fields used without translation
- Ambiguity in core claims due to undefined terms

**Measurement Method:**
- Detect definition patterns (":=", "defined as", "we define", "let X be", glossary sections)
- Track defined terms through document — flag meaning shifts
- Check equations for undefined variables
- Detect domain-specific jargon used without context
- Measure ratio of defined terms to total technical terms used

**GPT Rule Mapping:** "State premises explicitly." "Define every variable before you use it." "If you borrow a term, say you're borrowing it."

**Score Anchors:**
- +1.0: All terms defined, variables specified with domains/ranges, borrowed terms flagged, zero ambiguity
- +0.5: Most terms defined, some variables under-specified, minor ambiguity
- 0.0: Cannot determine
- -0.5: Significant terms undefined, variable meanings unclear, jargon unexplained
- -1.0: Core terms undefined, pervasive ambiguity, reader must guess meanings

---

### F8: GENTLENESS (Prautes) — Graceful Degradation Under Attack

**Structural Definition:** The theory can be rejected without the entire framework collapsing. Individual claims can be challenged without threatening the whole structure. The theory offers clean rejection paths. It doesn't hold the reader hostage with "accept everything or nothing."

**Positive Indicators:**
- Explicit modularity ("even if Section 3 fails, Sections 1-2 and 4-5 stand independently")
- Clean separation between core axioms and derived claims
- Individual predictions can fail without killing the framework
- Author acknowledges which parts are strongest and which are most speculative
- Graceful narrowing of scope when challenged

**Negative Indicators:**
- Monolithic argument where one break destroys everything
- "If you reject X, you must also reject all of physics" style rhetoric
- No distinction between core and peripheral claims
- All-or-nothing presentation
- Theory treats every component as equally load-bearing

**Measurement Method:**
- Detect modularity language ("independent of," "even if," "separable from")
- Check for strength gradations across claims (some marked as speculative, some as established)
- Identify dependency chains — are they linear (fragile) or networked (robust)?
- Count graceful degradation statements
- Detect "accept all or nothing" framing

**GPT Rule Mapping:** "Allow rejection without collapse." "Not every claim is equally load-bearing — say which ones are."

**Score Anchors:**
- +1.0: Explicit modularity, clear core/peripheral distinction, graceful degradation paths, no hostage-taking
- +0.5: Some modularity, partial strength gradation
- 0.0: Cannot determine
- -0.5: Mostly monolithic, little graceful degradation
- -1.0: Fully monolithic, all-or-nothing, rejection = total collapse

---

### F9: SELF-CONTROL (Egkrateia) — Claim Bounding

**Structural Definition:** The theory says what it claims and claims only what it can support. It does not overreach. When evidence supports a modest conclusion, it draws a modest conclusion. It knows where its domain ends.

**Positive Indicators:**
- Explicit scope statements ("this framework does not claim to solve...")
- Claims calibrated to evidence strength
- "We do not claim..." or "this does not explain..." disclaimers
- Careful distinction between "suggests" and "proves"
- Boundary markers between established results and speculation

**Negative Indicators:**
- Grand claims with thin evidence
- "This proves..." when the evidence only "suggests"
- No scope limitations stated
- Theory claims to solve everything
- Speculation presented as established fact

**Measurement Method:**
- Count scope limitation statements
- Detect overclaim language ("proves," "establishes," "demonstrates" vs. "suggests," "indicates," "is consistent with")
- Measure evidence-to-claim ratio (how much evidence per unit claim)
- Check for explicit boundary markers between speculation and established results
- Detect "solves the hard problem" / "unified theory of everything" style overclaims without proportionate evidence

**GPT Rule Mapping:** "Don't overclaim validation." "The difference between 'suggests' and 'proves' is the difference between science and propaganda."

**Score Anchors:**
- +1.0: Precise scope, claims calibrated to evidence, explicit non-claims, clear speculation markers
- +0.5: Mostly bounded, occasional overreach, some scope statements
- 0.0: Cannot determine
- -0.5: Frequent overclaiming, weak scope statements, speculation-as-fact
- -1.0: Massive overclaiming, no bounds, evidence doesn't support conclusions

---

### F10: TRUTH (Aletheia) — Evidence-Claim Alignment

**Structural Definition:** The theory's claims are proportionate to its evidence. What it says is supported by what it shows. Citations are real and relevant. Data is presented honestly. The evidence actually supports the specific claims being made, not just adjacent claims.

**Positive Indicators:**
- Citations point to real, verifiable sources
- Data presented with uncertainty bounds
- Statistical claims include sample sizes, p-values, confidence intervals
- Evidence directly supports the specific claim it's cited for (not just the general topic)
- Negative results or limitations honestly reported

**Negative Indicators:**
- Claims without supporting evidence
- Evidence cited doesn't actually support the specific claim
- Cherry-picked data (only favorable results shown)
- Statistics without context (p-value without sample size)
- No uncertainty quantification

**Measurement Method:**
- Count evidence units (citations, data points, experimental references) per claim
- Check citation specificity (does the cited work actually address the claim?)
- Detect statistical claims and check for completeness (p-value + n + CI)
- Measure claims-to-evidence ratio
- Detect uncertainty language ("approximately," "within error bars," "±")

**GPT Rule Mapping:** "Every claim needs either evidence or an explicit flag that it's a hypothesis." "Report your uncertainties."

**Score Anchors:**
- +1.0: Every claim evidenced, statistics complete, uncertainties quantified, limitations honest
- +0.5: Most claims supported, some statistics incomplete, partial uncertainty reporting
- 0.0: Cannot determine
- -0.5: Significant unsupported claims, incomplete statistics, cherry-picking
- -1.0: Claims unsupported, evidence misrepresented, no uncertainty acknowledgment

---

### F11: WISDOM (Sophia) — Hierarchical Understanding

**Structural Definition:** The theory knows what's important and what's detail. It operates at the right level of abstraction. It can zoom out to show the big picture and zoom in to show the mechanism. It knows which results are load-bearing and which are decorative.

**Positive Indicators:**
- Clear hierarchy: axioms → theorems → predictions → applications
- Big-picture framing before detailed argument
- Explicit marking of load-bearing vs. decorative results
- Ability to summarize the theory at multiple levels (one sentence, one paragraph, one page)
- Strategic ordering — most important results first, implications and details follow

**Negative Indicators:**
- Flat presentation (everything equally weighted)
- No distinction between core insights and supporting details
- Reader can't tell what matters most
- Theory buries the lead — critical insight hidden in Section 7
- No summary or overview, just sequential detail dump

**Measurement Method:**
- Check for hierarchical structure (numbered axioms/laws/theorems)
- Detect "the key insight is..." or "the central claim is..." framing
- Measure whether abstract/introduction captures the essential argument
- Check for load-bearing markers
- Assess structural nesting depth (framework → laws → corollaries → applications)

**GPT Rule Mapping:** "Lead with the insight, not the derivation." "The reader should know what matters within the first paragraph."

**Score Anchors:**
- +1.0: Clear hierarchy, load-bearing results marked, multi-level summaries, strategic ordering
- +0.5: Some hierarchy, partial prioritization
- 0.0: Cannot determine
- -0.5: Flat presentation, buried lead, no prioritization
- -1.0: Completely unstructured, reader cannot identify what matters

---

### F12: GRACE (Charis) — Error Tolerance and Recovery

**Structural Definition:** The theory handles edge cases, exceptions, and apparent counterexamples with structural grace. It doesn't break at the boundaries. When confronted with anomalies, it either assimilates them into the framework or explicitly acknowledges them as open problems — it doesn't pretend they don't exist.

**Positive Indicators:**
- Edge cases explicitly addressed
- Apparent counterexamples discussed and either resolved or acknowledged
- Framework degrades gracefully at boundaries (limiting cases make sense)
- Error bars and uncertainty treated as information, not as threats
- "This is an open problem" stated honestly where true

**Negative Indicators:**
- Edge cases ignored
- Counterexamples dismissed without engagement
- Framework breaks at boundaries with no acknowledgment
- Uncertainty treated as failure rather than as information
- Perfect-certainty claims on messy data

**Measurement Method:**
- Detect edge case handling ("in the limit," "boundary condition," "special case")
- Check for counterexample engagement
- Detect "open problem" acknowledgments
- Check mathematical limiting cases (does the framework reduce properly when variables approach 0 or ∞?)
- Detect uncertainty acknowledgment vs. uncertainty denial

**GPT Rule Mapping:** "Handle your edge cases." "Open problems honestly stated are worth more than problems swept under the rug."

**Score Anchors:**
- +1.0: Edge cases handled, counterexamples engaged, limiting cases correct, open problems acknowledged
- +0.5: Some edge cases addressed, partial counterexample engagement
- 0.0: Cannot determine
- -0.5: Edge cases mostly ignored, counterexamples dismissed
- -1.0: Boundaries unaddressed, counterexamples denied, false precision everywhere

---

## 5. FRUIT-TO-TRIAD MAPPING (Preserved)

The existing Triad mapping architecture is sound. Each Fruit feeds Π (Polis), A (Anthropos), and Λ (Logos) through weighted channels. What changes is the *input signal*, not the *mapping weights*.

| Fruit | Primary Triad | Secondary | Tertiary |
|---|---|---|---|
| F1 Love | Λ (Integration) | A (Service) | Π (Bridge-building) |
| F2 Joy | Λ (Generativity) | A (Research spirit) | Π (Community benefit) |
| F3 Peace | Λ (Non-contradiction) | A (Consistency) | Π (Stability) |
| F4 Patience | Λ (Derivation depth) | A (Thoroughness) | Π (Accessibility) |
| F5 Kindness | A (Intellectual charity) | Π (Engagement) | Λ (Steelmanning) |
| F6 Goodness | Π (Constructive value) | Λ (Standalone tools) | A (Methodology) |
| F7 Faithfulness | Λ (Definitions) | A (Consistency) | Π (Reliability) |
| F8 Gentleness | A (Modularity) | Λ (Clean rejection) | Π (Graceful scope) |
| F9 Self-Control | Λ (Claim bounding) | A (Epistemic humility) | Π (Scope discipline) |
| F10 Truth | Λ (Evidence alignment) | Π (Verifiability) | A (Honest reporting) |
| F11 Wisdom | Λ (Hierarchy) | A (Strategic ordering) | Π (Clarity) |
| F12 Grace | A (Error tolerance) | Λ (Edge case handling) | Π (Open problem acknowledgment) |

---

## 6. EDB INTEGRATION INTO SYSTEM 2

System 3's Epistemic Drift Bands should be adopted into System 2's scoring. When scoring a multi-domain paper:

1. Parse the document for domain markers (physics equations, scripture references, consciousness claims, ethical arguments)
2. Assign EDB tolerance vectors to each detected domain
3. Score each Fruit *within the tolerance band of the domain it appears in*

**Example:** A Genesis paper's physics claims (R²=0.888 lifespan decay) get scored for Truth with physics-level rigor (full statistical apparatus required). The same paper's theological claims (Adam's Fall as quantum decoherence event) get scored for Truth with theology-level tolerance (internal consistency and scriptural alignment required, not laboratory replication).

This prevents the current failure mode where physics expectations are applied uniformly to theological content, producing artificially low scores across the board.

### Default EDB Vectors (from System 3)

| Domain | Rigor | Empirical | Interpretive | Temporal | Falsifiable |
|---|---|---|---|---|---|
| Physics | 5 | 5 | 1 | 5 | 5 |
| Scripture | 5 | 4 | 1 | 5 | 2 |
| Information | 4 | 3 | 3 | 3 | 3 |
| Evidence | 4 | 4 | 2 | 4 | 4 |
| Theology | 2 | 1 | 4 | 2 | 1 |
| Consciousness | 1 | 1 | 5 | 1 | 0 |
| Ethics | 1 | 0 | 5 | 1 | 0 |

---

## 7. IMPLEMENTATION PRIORITY

### Phase 1: Section Boundary Parser (Unblocks everything)

**Build first.** Without this, all scores remain contaminated. Simple regex-based section classifier. Test on Genesis papers where contamination is confirmed.

**Files to modify:** `unified_scorer.py` — add `split_document()` preprocessing step before any scoring.

**Validation:** Re-score Genesis papers. Confirm χ rises from 3.0 to 6.0+ range. Confirm Non-Contradiction constraint flips from Violated to Satisfied.

### Phase 2: Fruit Rubric YAML Files (12 files)

Replace `fruit_matrix.yaml` with 12 individual YAML files, one per Fruit. Each file contains the structural definition, positive/negative indicators, and measurement rules from §4 above.

**Files to create:**
```
rubrics/
├── f01_love_rubric.yaml
├── f02_joy_rubric.yaml
├── f03_peace_rubric.yaml
├── f04_patience_rubric.yaml
├── f05_kindness_rubric.yaml
├── f06_goodness_rubric.yaml
├── f07_faithfulness_rubric.yaml
├── f08_gentleness_rubric.yaml
├── f09_self_control_rubric.yaml
├── f10_truth_rubric.yaml
├── f11_wisdom_rubric.yaml
└── f12_grace_rubric.yaml
```

**Validation:** Score 3–5 papers where scores are known from human evaluation. Confirm detector catches what a human reader would catch. Confirm six Fruits that were returning 0.00 now return non-zero scores.

### Phase 3: EDB Integration

Add domain detection and EDB tolerance vectors to System 2 scoring. Pull EDB framework from System 3.

### Phase 4: Master Score Matrix

Build the integration layer that combines System 1 (WQ), System 2 (χ/κ/ρ), and System 3 (Similarity/EDB) into the Paper Registry.

### Phase 5: Statistical Validation

Run all three systems on the full vault. Compare scores against human rankings. Calibrate weights. Publish methodology.

---

## 8. FILE LOCATIONS

| Component | Path |
|---|---|
| unified_scorer.py | `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\scripts\from_Note\unified_scorer.py` |
| fruit_matrix.yaml (current) | `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\scripts\from_Note\rubrics\fruit_matrix.yaml` |
| theophysics_compare.py | To be placed at `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\scripts\theophysics_compare.py` |
| vault_metrics.py | `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\scripts\from_Note\vault_metrics.py` |
| Fruits Evaluator Prompt | `O:\_Theophysics_v3\00_SYSTEM\02_PROMPTS\EVALUATION_BUNDLE\05_INTEGRATED_FRUITS_EVALUATOR.md` |
| Cross Domain Fruits Score | `O:\_Theophysics_v3\GO FOLDER\Cross_Domain_Fruits_Score\` |
| Supplementary Code Package | `O:\_Theophysics_v3\GO FOLDER\Cross_Domain_Fruits_Score\docs\SUPPLEMENTARY_CODE_PACKAGE.md` |
| Output Excel | `O:\_Theophysics_v3\00_SYSTEM\01_ENGINE\scripts\from_Note\outputs\Unified_Scorer_SMART.xlsx` |

---

## 9. KNOWN ISSUES LOG

| Issue | Impact | Fix | Phase |
|---|---|---|---|
| Critique contamination | 3 papers capped at χ=3.0 falsely | Section boundary parser | 1 |
| 6 Fruits return 0.00 | Half the instrument panel dark | Structural rubric rebuild | 2 |
| Triad centers at 0.5 | All Π/A/Λ values meaningless | Follows from rubric fix (non-zero inputs) | 2 |
| No domain-adjusted scoring | Physics rigor applied to theology | EDB integration | 3 |
| Three systems disconnected | No unified view of paper readiness | Master Score Matrix | 4 |
| No human-validated calibration | Scores not benchmarked against known-good rankings | Statistical validation | 5 |

---

*This document supersedes all prior scoring system documentation. Implementation begins with Phase 1.*

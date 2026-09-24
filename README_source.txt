# The Unofficial Guide

Tiye Gordon — selected corpus: `city_guides`

---

## Unit 1

### What This Does

This system uses the `city_guides` corpus to answer questions about places to eat, walking, regional transport, seasons, and accessibility. The guides are Markdown files organized by place or activity, with headings and paragraphs that carry the details needed for an answer. I tested questions about train tickets, parking, attractions, hospitals, and travel between towns. The system retrieves relevant parts of the guides to support its answers.

#### Questions in `questions.py`

These five questions and expected answers come from my `QUESTIONS` list. The expected answers are test targets, not verified system outputs. I will compare them with the source and the system's actual response.

| Question | Expected answer from my notes |
|---|---|
| When is the best time to book railway tickets at a cheaper-than-normal rate? | The day before or when booking a week ahead. |
| Which cities have free parking? | Kestreford's lower car park area is the only city with free parking. |
| What are some fun things visitors can do while in Kestreford and Marchwood? | The Sunday morning market square is the main event in Kestreford and has run continuously since the 1400s. In Marchwood, the city museum is an excellent visitor attraction. The canal walk from Northgate to the old lock is recommended by residents when asked by visitors. |
| Where is the hospital located? | The nearest hospital is in Brightwater. It has a minor injuries unit locally with limited hours. |
| What is the best means of transportation with the shortest travel time from Brightwater to Givens Mill? | The shortest route from Brightwater to Givens Mill takes 20 minutes by car. |

The `OUT_OF_SCOPE` list in `questions.py` asks about Mongolia's capital, changing oil in a diesel engine, the 1994 World Cup winner, ibuprofen dosage, and writing a Rust `for` loop. These are the five questions used to test whether the relevance gate refuses unrelated requests:

1. What is the capital of Mongolia?
2. How do I change the oil in a diesel engine?
3. Who won the 1994 World Cup?
4. What is the recommended dosage of ibuprofen for a headache?
5. How do I write a for loop in Rust?

**Check before running the evaluation:** The supplied `questions.py` spells the place **Kestreford**, while the guide and sample chunk spell it **Kestrelford**. Chunk 4 says the market is on **Saturday**, while `expects` says **Sunday**. Correct these mismatches in `questions.py` after checking the source; otherwise a source-supported answer may be marked wrong. The railway, hospital, and route expectations also need checking against the guides.

### Chunking Strategy

- **Chunk size:** Maximum of 800 characters per finished chunk, measured in characters.

- **Overlap:** [Record the overlap actually implemented in `chunker.py`; the supplied notes do not establish a number.]

I examined the Markdown guides and chose a boundary order of document title, section heading, paragraph, then sentence. I want each chunk to retain its document and section context, so a place name, exception, or comparison stays with the statement it explains. I split at paragraph breaks where possible. If a paragraph is too long for the 800 character limit, I use sentence boundaries. The heading can provide context without becoming a chunk by itself. This reflects how the guides organize answers across paragraphs, including cases where the useful advice depends on a nearby exception.

The baseline recorded in my measurement prompt was **14 documents, 28,958 source characters, 51 chunks, 650 characters on average, shortest 24 and longest 800**, produced by `chunker.py::fallback_split`. A later screenshot shows **14 documents and 94 chunks**, produced by `chunker.py::split_documents`, with a longest chunk of **762** characters. These counts describe different splitting runs; they do not establish that retrieval improved. [Confirm the current code, index output, and overlap before submission.]

### Sample Chunks

The chunk command reported **94 chunks total** and displayed these five spread across the corpus.

#### Chunk 1 — source: `guide_accessibility.md#0` — produced by: `chunker.py::split_documents`

```text
# Getting around the region with limited mobility

An honest assessment rather than a promotional one. Some of these places are
difficult and it is better to know in advance.
```

#### Chunk 2 — source: `guide_corry_vale.md#5` — produced by: `chunker.py::split_documents`

```text
# Corry Vale

### Where to stay

Perhaps thirty beds in the entire valley, spread across two pubs and a handful of farmhouse rooms. In summer these are booked months ahead. Camping is permitted on two marked fields and nowhere else.
```

#### Chunk 3 — source: `guide_givens_mill.md#2` — produced by: `chunker.py::split_documents`

```text
# Givens Mill

### Getting around

Everything is on one street along the river. The mill is at one end and the church at the other, eight minutes apart. The riverside path continues in both directions for as far as you want to walk.
```

#### Chunk 4 — source: `guide_kestrelford.md#4` — produced by: `chunker.py::split_documents`

```text
# Kestrelford

### What to see

The market square on a Saturday morning is the main event and has run continuously since the 1400s. The parish church has a 13th-century tower you can climb for £2. The old trackbed walk runs six miles to the next village along an easy gradient and is the best half-day here.
```

#### Chunk 5 — source: `guide_pellew_sands.md#6` — produced by: `chunker.py::split_documents`

```text
# Pellew Sands

### When to go

June and September for the beach without the crowds. July and August are busy and the town is at its most itself, for better and worse. Winter is bleak, largely closed, and has a following among people who like that sort of thing.
```

Each displayed chunk reads as a complete thought on its own: chunk 1 introduces the accessibility guide's scope; chunks 2–5 include a place and section heading with the information that follows. This judgment applies to these five displayed chunks, not automatically to all 94.

### Sample Answer

- **Question:** Where can I find good food for less near Brightwater's riverside strip?

- **Answer from the attached run:** Comparable food is available on Corry Lane, two streets inland, for about a third less.

- **Source shown in the run:** `guide_brightwater.md` and `guide_eating.md` [copy the exact source line from the terminal output before submitting].

**My relevance cutoff:** The saved `before` report confirms **0.6** for that evaluation. This refused all five out-of-scope questions, but also refused two of my five intended in-corpus questions, at distances 0.6075 and 0.6410. The covered questions' best distances range from 0.3785 to 0.6410; the out-of-scope questions range from 0.803 to 0.975. A cutoff between 0.6410 and 0.803 might separate these particular ten best distances, but I have not tested a changed cutoff or checked whether those two retrieved chunks actually contain the answers. [Confirm the current value in `config.py` before calling it final.]

| Question | In corpus? | Best distance |
|---|---|---:|
| Where can I find good food for less near Brightwater's riverside strip? | Yes | 0.293 |
| If I eat outside Marchwood, how late can I expect kitchens to serve? | Yes | 0.317 |
| Why might I need to travel to Northgate for a good meal in Marchwood? | Yes | 0.257 |
| What should I know about accessibility in Marchwood? | Yes | 0.447 |
| Does the guide say where to eat breakfast in Brightwater? | [Check: the displayed answer says the guides do not mention it] | 0.473 |

These five distances come from separate questions in the attached screenshots; they are **not** the distances for the five `QUESTIONS` above or the five `OUT_OF_SCOPE` questions. The last screenshot question appears unsupported despite passing the 0.6 distance gate. The actual ten-question `before` run is recorded in Unit 2 below. In that run, the two highest distances for covered questions (0.608 and 0.641) are below the lowest out-of-scope distance (0.803), leaving a numerical gap between the groups. [Confirm the final cutoff in `config.py` and inspect the actual answers and refusals before claiming that the gate performed correctly on covered questions.]

### How I Used AI

1. **Working through my logic with `/plan`.** I used the `/plan` option to talk through how I wanted to divide the Markdown guides. I specifically asked AI to help me reason about my choices, not to give me the answer or write a script at that stage. I began by considering document titles, headings, paragraphs, and sentences. The discussion helped me separate **where a split can happen** from **how large a finished chunk can be**. After examining my retrieval results, I proposed testing sentence-centered chunks with nearby sentences for context. I made that decision by considering both the missed railway answer and the Marchwood exception, where a nearby sentence might still fail to explain the broader rule.

2. **Calculations and corpus review.** I asked AI to inspect the original `city_guides` Markdown files and help calculate the lengths of documents, sections, paragraphs, and sentences. I asked for measurements and explanations rather than a script or a prescribed chunking strategy. Later, I used it to review the 94 before-index chunks against the original guides, calculate the word-boundary result (94/94), and identify where the source contained facts missing from the top-five retrieval results. I also asked it to count sentences in each original guide: 317 sentences overall, averaging 84.24 characters, with a shortest sentence of 8 and a longest of 197. These checks gave me evidence to evaluate my own chunking idea.

3. **Testing the chunk limit and requesting implementation help.** After working through the strategy, I explicitly asked AI to generate a revised `chunker.py` that centers a chunk on one sentence and includes its immediate neighbors from the same section when they fit. I then asked AI to measure the resulting chunks against the original guides. The longest observed chunk was **436 characters**, including its title, heading, and sentence context; this is a chunk measurement, not the longest individual sentence (197 characters). I chose to lower the maximum from 800 to 436 based on that observation. On the measured guides, this did not shorten any chunks, because none exceeded 436. My earlier `/plan` request was for help thinking through the method; I requested code generation later as a separate step.

---

## Unit 2

### Evaluation Criteria and Targets

I will evaluate the same five criteria before and after my improvement. My five answerable questions come from `QUESTIONS`; the five unrelated questions come from `OUT_OF_SCOPE` in `questions.py`. Results below must come from actual runs, not these targets.

| # | Criterion | Calculation and decision rule | Target |
|---|---|---|---|
| 1 | Hit Rate@5 (retrieved chunk contains the answer) | For each of the five answerable questions, check whether at least one of the top five retrieved chunks contains enough evidence for its expected answer. Divide successful questions by five. | At least 4/5 (80%) |
| 2 | Citation coverage | Count generated answers that name at least one source, divided by generated answers produced for the five answerable questions. | 5/5 (100%) |
| 3 | Out-of-scope rejection rate | Count `OUT_OF_SCOPE` questions stopped by the relevance gate, divided by five. | At least 4/5 (80%) |
| 4 | Word boundary integrity (WBI) | Count chunks whose beginning and end do not cut through a word, divided by all indexed chunks. Check against the original text rather than judging a displayed fragment alone. | 100% |
| 5 | Semantic boundary alignment rate (SBAR) | Count chunks whose content begins and ends at meaningful document, section, paragraph, or sentence boundaries and keeps any necessary heading and answer context, divided by all indexed chunks. Inspect the actual chunk text and its neighboring source text. | At least 80% |

For criterion 3, this rate measures rejection of the five specifically selected out-of-scope questions. It is a true negative rate only for that test set. For criterion 2, naming a source does not establish that the source supports the answer. I will inspect citation correctness (whether cited sources support the claims) and citation completeness (whether factual claims are cited) when reviewing generated answers, but those are separate checks and are not additional scored criteria here.

The 80% targets for Hit Rate@5 and SBAR are starting goals. They measure different things: a chunk can end cleanly yet never be retrieved, and a retrieved chunk can contain an answer even if another chunk has a poor boundary. A WBI score of 100% therefore does not guarantee an SBAR score of 80% or a Hit Rate@5 of 80%. Chunking affects later embedding, retrieval, and answer generation, so I will examine failures at each stage before changing the chunking rules.

### Run Log — Before

- **Command:** `python run_eval.py --label before`  
- **Saved run evidence:** `results/run_2026-09-23_2031_before.md`  
- **Produced by:** `run_eval.py::main`; out-of-scope gate check: `run_eval.py::check_out_of_scope`; retrieval: `store.py::search`.  
- **Settings in saved report:** `city_guides`, variant `default`, top-k 5, cutoff 0.6, three runs per question with caching off.  
- **Scoring status:** The command reported `No scorer.py found — running unscored. Verdict column will be blank.` The three run columns below refer to the three runs within this one invocation; they are not three separately saved evaluation files. [Commit the generated result file in the project repository as requested by the tool output.]

| Covered question from `QUESTIONS` | Run 1 best distance | Run 2 best distance | Run 3 best distance | Scored verdict |
|---|---:|---:|---:|---|
| When is the best time to book railway tickets at a cheaper-than-normal rate? | 0.608 | 0.608 | 0.608 | — |
| Which cities have free parking? | 0.641 | 0.641 | 0.641 | — |
| What are some fun things visitors can do while in Kestreford and Marchwood? | 0.427 | 0.427 | 0.427 | — |
| Where is the hospital located? | 0.469 | 0.469 | 0.469 | — |
| What is the best means of transportation with the shortest travel time from Brightwater to Givens Mill? | 0.379 | 0.379 | 0.379 | — |

| Out-of-scope question from `OUT_OF_SCOPE` | Best distance | Gate result |
|---|---:|---|
| What is the capital of Mongolia? | 0.803 | Refused |
| How do I change the oil in a diesel engine? | 0.888 | Refused |
| Who won the 1994 World Cup? | 0.975 | Refused |
| What is the recommended dosage of ibuprofen for a headache? | 0.835 | Refused |
| How do I write a for loop in Rust? | 0.836 | Refused |

The run reported **gate refused 5 of 5** out-of-scope questions. Two intended in-corpus questions were also refused in all three runs: rail tickets at **0.6075** and free parking at **0.6410**. The other three questions passed the gate. The saved report gives answers and retrieved **filenames**, but no retrieved chunk text; filenames alone cannot establish whether one of the top five chunks contains each answer. [Inspect the retrieved chunk texts for criterion 1 and the indexed chunks for criteria 4 and 5.]

#### Retrieval check for criterion 1: rail tickets

Command: `python3 app.py --corpus city_guides retrieve "When is the best time to book railway tickets at a cheaper-than-normal rate?"`

| Rank | Distance | Source | Displayed preview |
|---:|---:|---|---|
| 1 | 0.6075 | `guide_kestrelford.md` | `# Kestrelford  ## When to go  Late spring and early ...` |
| 2 | 0.6363 | `guide_eating.md` | `# Eating across the region  ## Markets  Kestrelford'...` |
| 3 | 0.6414 | `guide_marchwood.md` | `# Marchwood  ## Getting around  A tram network of fo...` |
| 4 | 0.6711 | `guide_givens_mill.md` | `# Givens Mill  ## When to go  The mill runs March to...` |
| 5 | 0.7078 | `guide_marchwood.md` | `# Marchwood  ## When to go  Any time. This is the on...` |

The command reported: `Gate: best distance 0.608 is over the 0.6 cutoff — refusing`. These previews do **not** display the full text of the five chunks. Therefore this question's Hit Rate@5 result is **undetermined** from this output: I must inspect the full chunks to decide whether one contains the ticket booking answer. The refusal establishes a gate outcome, not whether retrieval found evidence.

#### Retrieval check for criterion 1: free parking

Command: `python3 app.py --corpus city_guides retrieve "Which cities have free parking?"`

| Rank | Distance | Source | Displayed preview |
|---:|---:|---|---|
| 1 | 0.6410 | `guide_marchwood.md` | `# Marchwood  ## What to see  The city museum is free...` |
| 2 | 0.6518 | `guide_halden_bay.md` | `# Halden Bay  ## Getting there  The coast road is th...` |
| 3 | 0.6520 | `guide_kestrelford.md` | `# Kestrelford  ## Getting around  Everything is with...` |
| 4 | 0.6970 | `guide_accessibility.md` | `# Getting around the region with limited mobility  #...` |
| 5 | 0.6994 | `guide_givens_mill.md` | `# Givens Mill  ## Getting there  No station and no b...` |

The command reported: `Gate: best distance 0.641 is over the 0.6 cutoff — refusing`. The third result is from the Kestrelford guide, but the preview does not show its parking statement. This question's Hit Rate@5 result is **undetermined** until I read the complete retrieved chunk. A source filename alone does not establish that the relevant answer is inside this particular chunk.

#### Retrieval check for criterion 1: attractions in Kestrelford and Marchwood

Command: `python3 app.py --corpus city_guides retrieve "What are some fun things visitors can do while in Kestreford and Marchwood?"`

| Rank | Distance | Source | Displayed preview |
|---:|---:|---|---|
| 1 | 0.4272 | `guide_accessibility.md` | `# Getting around the region with limited mobility  #...` |
| 2 | 0.4436 | `guide_kestrelford.md` | `# Kestrelford  ## What to see  The market square on ...` |
| 3 | 0.4484 | `guide_kestrelford.md` | `# Kestrelford  ## Where to stay  Two inns on the squ...` |
| 4 | 0.4605 | `guide_marchwood.md` | `# Marchwood  ## Where to stay  Plentiful and, outsid...` |
| 5 | 0.4662 | `guide_eating.md` | `# Eating across the region  ## Opening hours  This c...` |

The gate passed this question at a best distance of **0.4272**. The rank-2 preview matches the Kestrelford **What to see** sample chunk above, which contains the Saturday market and other attractions. The question also asks about Marchwood, so this partial evidence alone does not settle whether at least one retrieved chunk contains the **complete** expected answer. The `questions.py` expectation says Sunday, contrary to the Kestrelford chunk's Saturday. [Inspect the full top-five chunks and clarify whether the criterion judges one chunk containing the entire multi-town answer or the top-five set supplying its parts.]

#### Retrieval check for criterion 1: hospital location

Command: `python3 app.py --corpus city_guides retrieve "Where is the hospital located?"`

| Rank | Distance | Source | Displayed preview |
|---:|---:|---|
| 1 | 0.4695 | `guide_accessibility.md` | `# Getting around the region with limited mobility  #...` |
| 2 | 0.5768 | `guide_givens_mill.md` | `# Givens Mill  ## Practical notes  Cash is still use...` |
| 3 | 0.5776 | `guide_halden_bay.md` | `# Halden Bay  ## Practical notes  Cash is still usef...` |
| 4 | 0.5779 | `guide_kestrelford.md` | `# Kestrelford  ## Practical notes  Cash is still use...` |
| 5 | 0.5932 | `guide_thornby_wells.md` | `# Thornby Wells  ## Practical notes  Cash is still u...` |

The gate passed at a best distance of **0.4695**. The earlier generated answer cites these files for different nearest hospitals depending on the starting location, but the previews above do not show those statements. Hit Rate@5 remains **undetermined** from this preview output. The question needs a location to define what *nearest* means before its expected answer can be judged reliably.

#### Retrieval check for criterion 1: Brightwater to Givens Mill

Command: `python3 app.py --corpus city_guides retrieve "What is the best means of transportation with the shortest travel time from Brightwater to Givens Mill?"`

| Rank | Distance | Source | Displayed preview |
|---:|---:|---|
| 1 | 0.3785 | `guide_brightwater.md` | `# Brightwater  ## Getting around  The town is walkab...` |
| 2 | 0.4089 | `guide_walking.md` | `# Walking in the region  ## Easy, on good surfaces  ...` |
| 3 | 0.4278 | `guide_givens_mill.md` | `# Givens Mill  ## Getting there  No station and no b...` |
| 4 | 0.4479 | `guide_corry_vale.md` | `# Corry Vale  ## Getting there  There is no public t...` |
| 5 | 0.4521 | `guide_regional_transport.md` | `# Getting around the region  ## Walking and cycling ...` |

The gate passed at a best distance of **0.3785**. The earlier generated answer gives a 20-minute drive and cites `guide_givens_mill.md`, which is the rank-3 retrieved source. The preview does not display the time comparison; the full-chunk inspection below resolves this question.

#### Full chunk inspection for criterion 1

I inspected the supplied output of `python3 app.py --corpus city_guides chunks -n 94`, produced by `chunker.py::split_documents`. This lists all 94 chunk texts. The `retrieve` output identifies **filenames and previews**, but does not print the chunk's `#` identifier; where one filename has several chunks, a filename match by itself does not prove which chunk was ranked.

| Question | Evidence in the full chunk listing | Judgment supported so far |
|---|---|---|
| Rail tickets | `guide_regional_transport.md#0` contains the day-before and week-ahead ticket rule, but **none** of the five retrieved filenames is `guide_regional_transport.md`. | **No**: the answer-bearing chunk was outside the top five. |
| Free parking | `guide_regional_transport.md#2` says Kestrelford's lower car park is free. `guide_thornby_wells.md#1` and `guide_accessibility.md#1` say parking in Thornby Wells is free for two hours. Rank 3 is `guide_kestrelford.md` under **Getting around**, whose listed chunk `#2` mentions the lower car park but does **not** say it is free. Rank 4 is an accessibility chunk whose `#` is not shown by retrieval. | **Undetermined** until rank 4's complete text is matched. The expected answer that Kestrelford is the *only* town with free parking is contradicted by the Thornby Wells passages. |
| Attractions | `guide_kestrelford.md#4` contains the Saturday market; `guide_accessibility.md#1` mentions Marchwood's city museum. The specific `guide_marchwood.md#4` **What to see** chunk contains the canal walk, but the retrieved Marchwood preview is **Where to stay**, so that answer-bearing chunk was not retrieved. | The top five contain **some**, but not all, of the requested attractions. With the current full-answer test, **No**. The Sunday expectation also contradicts the Saturday source. |
| Hospital | `guide_accessibility.md#4` says the nearest full hospital for the region is Marchwood; several town **Practical notes** chunks say Brightwater. The retrieved filenames and previews are consistent with these passages, but omit chunk IDs and the hospital sentences. | **Undetermined** for an exact chunk match; the question's missing starting location also makes the expected single hospital ambiguous. |
| Brightwater to Givens Mill | Rank 3 previews `guide_givens_mill.md` under **Getting there**. The complete `guide_givens_mill.md#1` **Getting there** chunk states that the weekday bus takes 30 minutes and driving takes 20 minutes. | **Yes**: the retrieved rank-3 chunk contains the answer. |

Current supported tally: **1 Yes, 2 No, 2 undetermined**, using the rule that the retrieved material must support the **complete** answer to each question. [Match the exact accessibility chunk IDs returned at ranks 4 and 1 for parking and hospital, then record the final numerator out of five. If the assignment instead permits the top-five chunks *together* to cover a multi-part answer, state that rule consistently before scoring.]

#### Chunk boundary inspection for criteria 4 and 5

I compared all **94** chunks displayed by `python3 app.py --corpus city_guides chunks -n 94` with their corresponding passages in the **14 original Markdown guides**. For word boundary integrity, I checked the first and last word of each chunk against the source passage. **94/94 (100%)** begin and end at complete words; none cuts a word in half.

For semantic boundary alignment, I used the stated structural rule: the chunk starts with the document title, retains its section heading where there is one, and ends at a complete sentence rather than stopping mid-sentence or mid-paragraph. The guide introductions remain complete. **94/94 (100%)** meet that boundary rule, exceeding the 80% target of at least **76/94**. This is a judgment about the observed chunk divisions; it does not show that every question's answer is retrieved. For example, the ticket booking rule remains complete in `guide_regional_transport.md#0` but was absent from that question's top-five retrieval results.

The indexed chunks are fixed for this before evaluation, so the same **94/94** inspection result is recorded in all three run columns. It is one deterministic inspection repeated in the table, not three separate human reviews. The evidence comes from the `app.py chunks` output attributed to `chunker.py::split_documents` and comparison with the original `guide_*.md` files.

#### Real output from the before report

Produced by `run_eval.py::main`, calling `store.py::search` for retrieval and the gate before answer generation. The excerpts below are actual answers from `results/run_2026-09-23_2031_before.md`; they are not descriptions of the output.

**Rail tickets, run 1 — refused by the gate at 0.6075:**

```text
I don't have enough information about that.
```

**Free parking, run 1 — refused by the gate at 0.6410:**

```text
I don't have enough information about that.
```

**Attractions, run 1 — passed the gate at 0.4272:**

```text
In Kestrelford, visitors can check out the Saturday morning market square, climb the parish church's 13th-century tower, and do the old trackbed walk (guide_kestrelford.md). In Marchwood, visitors can explore the city museum and the covered market, both of which are step-free (guide_accessibility.md).
```

**Hospital, run 1 — passed the gate at 0.4695:**

```text
Depending on the location referenced:
- For the region generally, the nearest full hospital is in Marchwood (`guide_accessibility.md`).
- For Givens Mill, Halden Bay, Kestrelford, and Thornby Wells, the nearest full hospital is in Brightwater (`guide_givens_mill.md`, `guide_halden_bay.md`, `guide_kestrelford.md`, `guide_thornby_wells.md`).
```

**Travel time, run 1 — passed the gate at 0.3785:**

```text
Driving is the fastest means of transportation from Brightwater to Givens Mill, taking 20 minutes (compared to the bus, which takes 30 minutes on weekdays). 

Source: guide_givens_mill.md
```

**Out-of-scope gate, deterministic pass:** `run_eval.py::check_out_of_scope` reported `refused` for each of the five questions listed above, or **5 of 5**. The source report records all three answers for each covered question; the examples here show run 1, and the summary table above records all three distances.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 1 yes, 2 no, 2 pending | Same retrieval; 1 yes, 2 no, 2 pending | Same retrieval; 1 yes, 2 no, 2 pending | MISSED: at most 3 of 5 could pass |
| 2. Every answer names a source | 5 of 5 | 3 of 5 questions returned cited answers; 2 refusals | 3 of 5; 2 refusals | 3 of 5; 2 refusals | MISSED against 5 of 5; all 9 generated answers cited a source |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 (same deterministic pass) | 5 of 5 (same deterministic pass) | MET on the reported gate result |
| 4. Word boundary integrity | 100% of chunks | 94/94 (100%) | 94/94 (same index) | 94/94 (same index) | MET |
| 5. Semantic boundary alignment rate | At least 80% of chunks | 94/94 (100%) | 94/94 (same index) | 94/94 (same index) | MET under stated boundary rule |

### Verdicts

[Mark MET only if the target holds in every applicable run.]

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MISSED | The rail answer chunk was not in the top five, and the attraction set omitted the canal-walk chunk. Even if both unresolved questions pass, the maximum is 3 of 5, below the 4-of-5 target. This is a manual judgment from the retrieval previews and full chunk listing, not a `scorer.py` verdict. |
| 2 | Every answer names a source | MISSED against 5 of 5 | In each run, the three generated answers named at least one source; the other two questions were refused and produced no cited answer. Measured only over generated answers, coverage is 9/9, but the stated 5-of-5 question target is unmet. |
| 3 | Gate stops out-of-corpus questions | MET on the reported gate result | The gate refused all five `OUT_OF_SCOPE` questions in the deterministic pass. The run was unscored, so this is my manual comparison with the 4-of-5 target, not a `scorer.py` verdict. |
| 4 | Word boundary integrity | MET | All 94 chunks match complete words at both ends of their source passage: 94/94, meeting the 100% target. |
| 5 | Semantic boundary alignment rate | MET under stated boundary rule | All 94 chunks preserve their document title, relevant heading where present, and complete sentence endings: 94/94, above the 80% target. This does not imply that the answer-bearing chunk appears in a question's top five. |

### Diagnoses

- **Gate:** Both the rail-ticket question (0.6075) and the parking question (0.6410) were above the 0.6 cutoff, so the gate refused them in all three runs before generation. This explains why only three of five intended questions produced cited answers. Raising the cutoff is a candidate change to test, not a demonstrated fix: it cannot make the missing railway chunk enter the top five.

- **Retrieval misses after chunk inspection:** The ticket booking fact is intact in `guide_regional_transport.md#0`, but that file is absent from the five retrieved results for the ticket question. For the attractions question, the Kestrelford market chunk was retrieved, while Marchwood's `guide_marchwood.md#4` canal-walk chunk was not. Both are retrieval ranking misses, not evidence of a word or sentence split. The filename-only retrieval output prevents an exact judgment for the parking and hospital accessibility chunks.

- **Question design and expected answers:** My attractions expectation says Sunday and spells the town Kestreford; the source-backed generated answer says Saturday and spells it Kestrelford. The hospital question does not name a starting town, and the generated answers explain that the nearest full hospital varies with location. These are problems with the question or expected answer, not evidence that the generator is wrong. [Verify the relevant source passages and record any correction to `questions.py` before the after evaluation.]

[The inspected chunks support the criterion 1 retrieval diagnosis above and show no misses under the defined boundary tests for criteria 4 and 5. Revisit these judgments only if the index or boundary definition changes.]

### The Improvement

- **Original proposal:** I considered splitting each section by sentence and carrying the document title and section heading into each piece. A smaller piece might make a specific fact easier to find. I also wanted nearby sentences for context: the Marchwood eating exception may lose its relationship to the general rule when isolated.

- **What I changed:** I prepared a revised `chunker.py` that centers each chunk on one sentence, adds the immediate preceding and following sentences from the same section when they fit, retains the title and heading, and uses a 436-character cap. The after report identifies its index as produced by `chunker.py::split_documents`. [Confirm the actual project `chunker.py` and indexed chunk count match this prepared revision before claiming these exact settings were used in the after run.]

- **Why I picked it:** The railway booking fact was intact in the corpus but absent from the before run's top five. I wanted to test whether a sentence-centered piece would rank higher. Neighboring sentences were intended to limit context loss. A cutoff change alone could not put an answer-bearing chunk into the top five.

#### Run Log — After

**Report header:** Produced by `run_eval.py::main`; retrieval by `store.py::search`; chunks from `chunker.py::split_documents`; `city_guides` default index; top-k 5; cutoff 0.6; three runs with caching off; 2026-09-23 21:57. The report says `scorer.py` was absent, so its question-level verdict cells are blank. [Add and commit its actual `results/run_..._after.md` filename.]

| Covered question | Best distance in each run | Observed answers |
|---|---:|---|
| Railway booking | 0.5184 | All three passed the gate and cited `guide_regional_transport.md` for booking a day or a week ahead. Run 2's wording about which option is cheaper is ambiguous. |
| Free parking | 0.4893 | All three passed the gate and cited free parking in Thornby Wells and Kestrelford. The original expected answer wrongly says only Kestrelford. |
| Kestrelford and Marchwood attractions | 0.4271 | All three passed the gate and cited Kestrelford activities, but incorrectly said Marchwood activities were not listed. |
| Hospital | 0.4224 | All three passed the gate and cited sources explaining that the relevant hospital depends on location. The question still lacks a starting location. |
| Brightwater to Givens Mill | 0.3356 | All three passed the gate, answered 20 minutes by car, and cited `guide_givens_mill.md`. |

The five out-of-scope questions were each refused in one deterministic pass: Mongolia **0.789**, diesel oil **0.890**, 1994 World Cup **0.914**, ibuprofen **0.833**, and Rust loop **0.781**. The five distances are all above the unchanged 0.6 cutoff.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | Pending full chunk inspection | Same retrieval; pending | Same retrieval; pending | Undetermined from filenames and answers alone |
| 2. Every answer names a source | 5 of 5 | 5 of 5 | 5 of 5 | 5 of 5 | MET for citation coverage |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5 of 5 | 5 of 5 (same deterministic pass) | 5 of 5 (same deterministic pass) | MET |
| 4. Word boundary integrity | 100% of chunks | 317/317 (100%) | 317/317 (same chunks) | 317/317 (same chunks) | MET under the stated word-edge check |
| 5. Semantic boundary alignment rate | At least 80% of chunks | Pending context review | Same chunks; pending | Same chunks; pending | Undetermined: sentence endings alone do not establish complete meaning |

**Real output from the after report, run 1 (produced by `run_eval.py::main`):**

```text
Railway tickets are cheaper when booked the day before than on the day, and considerably cheaper than that when booked a week ahead (guide_regional_transport.md).
```

```text
Based on the provided documents, Thornby Wells has free parking for two hours anywhere in town (`guide_accessibility.md`). Additionally, Kestrelford's lower car park is free (`guide_regional_transport.md`).
```

```text
Based on the provided documents, visitors in Kestrelford can visit the market square on a Saturday morning, climb the 13th-century tower at the parish church for £2, and take the six-mile old trackbed walk to the next village (source: `guide_kestrelford.md`). 

Regarding Marchwood, the documents do not list specific fun activities other than noting that almost everything there is indoors and nothing closes seasonally (source: `guide_marchwood.md`).
```

**Did it help?** The observed gate outcome improved for intended questions: before, two of five were refused; after, all five passed at the unchanged 0.6 cutoff. Every after answer named a source, compared with three cited answers and two refusals per before run. All five out-of-scope questions were still refused. Hit Rate@5 cannot yet be compared without the after top-five chunk texts. The attractions answer remains incomplete, showing that passing the gate and naming a source did not guarantee a complete answer.

### What's Still Broken

The Marchwood attractions answer misses the museum and canal walk even though the original guide lists them. [Inspect the after top-five chunks to find out whether retrieval omitted these facts or generation overlooked them.] The parking expectation incorrectly says only Kestrelford has free parking, and the hospital question omits the location from which “nearest” is judged. [Verify and document question or expectation corrections separately from the chunking change. Review the after chunks for criterion 5.]

### What I'd Do Differently

[After finishing the after chunk inspection, revisit one of the five criteria in light of both runs. Distinguish a retrieval miss from an incorrect expected answer or an ambiguous question.]

* **Word boundary integrity measurement note (before index):** I compared each of the 94 chunks printed by `python3 app.py --corpus city_guides chunks -n 94` with its passage in the corresponding original Markdown guide. All 94 chunk bodies matched source passages, and none began or ended in the middle of a word. I treated ordinary line breaks as spaces when matching text, because wrapping a line inside a chunk does not split a word across chunk boundaries. The calculation is **94 chunks with complete first and last words ÷ 94 total chunks × 100 = 100%**, so criterion 4 meets its 100% target. This check measures complete words at chunk edges; it does not establish that retrieval selected the right chunk or that every chunk contains a complete idea.

* **Word boundary integrity measurement note (after chunks):** The output of `python3 app.py --corpus city_guides chunks -n 400` displays **317 chunks** produced by `chunker.py::split_documents`. I compared each chunk body with the matching passage in its original `guide_*.md` file, treating display line wraps as spaces and excluding repeated Markdown title and section headings from the passage match. All **317/317** chunk bodies matched contiguous source text, and none began or ended in the middle of a word: **100%**. The three answer runs use the same chunk set, so this one structural measurement applies to each column. This establishes criterion 4 only; some overlapping chunks place neighboring sentences about different towns together, so criterion 5 still needs a separate context review.

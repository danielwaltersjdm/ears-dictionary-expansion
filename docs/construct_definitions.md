# Construct definitions - EARS Dictionary v2 expansion

Frozen: 2026-04-23. These definitions are the acceptance gate for every candidate
word or phrase considered for inclusion in v2. All raters (human or LLM ensemble)
classify candidates against these definitions and nothing else.

## Epistemic uncertainty

Uncertainty that is in principle reducible through additional knowledge, analysis,
skill, or effort. The speaker frames the outcome as *knowable* - "with more
information, or better analysis, I could be more certain." Language conveys:

- Assessability and model quality
- Degree of belief or confidence
- Clarity of understanding
- Informational sufficiency
- The possibility of learning or being persuaded

Example phrases in earnings-call context:
- "We believe Q3 will exceed consensus"
- "Based on our analysis..."
- "Visibility into the pipeline is good"
- "We are confident that demand will hold"
- "Our model suggests..."
- "It remains to be seen" (low-epistemic-confidence)

## Aleatory uncertainty

Uncertainty that is intrinsically random and irreducible even with perfect
information. The speaker frames the outcome as *stochastic* - "even knowing
everything, outcomes will still vary." Language conveys:

- Chance, probability, randomness as a world-property
- Dispersion, variability, fluctuation
- Probabilistic reasoning over outcomes
- Mechanical volatility (e.g., markets, commodities, weather)
- Distributional framing

Example phrases in earnings-call context:
- "Revenue fluctuates with commodity prices"
- "Probability of success is 30%"
- "FX volatility in the quarter"
- "Distribution of outcomes ranges from..."
- "By chance..."
- "The base rate for..."

## Classification rule for candidates

A candidate word or phrase is:
- **EPISTEMIC** if its primary use signals reducible, knowability-based uncertainty
- **ALEATORY** if its primary use signals irreducible, chance-based uncertainty
- **AMBIGUOUS** if it can signal either depending on context and the construct is not dominant
- **NEITHER** if it does not signal an uncertainty distinction at all

## Contested cases, resolved ex ante

- **"Likely"**: aleatory when used probabilistically ("likely outcome = 30%"), ambiguous when used as hedge ("likely we will announce"). If retained, requires bigram constraint to disambiguate.
- **"Expect"**: epistemic when forecasting-based ("we expect based on data"), ambiguous when generic ("we expect to release guidance next quarter"). If retained, requires bigram constraint.
- **"Sure"**: epistemic when assertion-of-confidence ("fairly sure, quite sure"), filler/ambiguous otherwise. Requires bigram constraint.
- **"Model"**: epistemic when referring to statistical/financial modeling of knowable quantities; ambiguous when aspirational ("role model"). Corpus disambiguates in earnings-call setting.
- **"Probability"**: always aleatory in context of outcome distributions.
- **"Distribution"**: aleatory when referring to probability distributions; ambiguous when referring to product distribution/logistics. Requires corpus-context check.

## References

- Fox, C. R., & Uelkuemen, G. (2011). Distinguishing two dimensions of uncertainty. In W. Brun, G. Keren, G. Kirkeboen, & H. Montgomery (Eds.), *Perspectives on thinking, judging, and decision making*. Universitetsforlaget.
- Tannenbaum, D., Fox, C. R., & Uelkuemen, G. (2017). Judgment extremity and accuracy under epistemic vs. aleatory uncertainty. *Management Science*, 63(2), 497-518.

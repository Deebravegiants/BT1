# [M] vLLM vulnerable to Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-j828-28rj-hfhp
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-j828-28rj-hfhp
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.6.3 <0.9.0

## Details
### Summary
A recent review identified several regular expressions in the vllm codebase that are susceptible to Regular Expression Denial of Service (ReDoS) attacks. These patterns, if fed with crafted or malicious input, may cause severe performance degradation due to catastrophic backtracking.

#### 1. vllm/lora/utils.py [Line 173](https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/lora/utils.py#L173)

https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/lora/utils.py#L173
**Risk Description:**
- The regex `r"\((.*?)\)\$?$"` matches content inside parentheses. If input such as `((((a|)+)+)+)` is passed in, it can cause catastrophic backtracking, leading to a ReDoS vulnerability.
- Using `.*?` (non-greedy match) inside group parentheses can be highly sensitive to input length and nesting complexity.

**Remediation Suggestions:**
- Limit the input string length.
- Use a non-recursive matching approach, or write a regex with stricter content constraints.
- Consider using possessive quantifiers or atomic groups (not supported in Python yet), or split and process before regex matching.

---

#### 2. vllm/entrypoints/openai/tool_parsers/phi4mini_tool_parser.py [Line 52](https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/entrypoints/openai/tool_parsers/phi4mini_tool_parser.py#L52)

https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/entrypoints/openai/tool_parsers/phi4mini_tool_parser.py#L52

**Risk Description:**
- The regex `r'functools\[(.*?)\]'` uses `.*?` to match content inside brackets, together with `re.DOTALL`. If the input contains a large number of nested or crafted brackets, it can cause backtracking and ReDoS.

**Remediation Suggestions:**
- Limit the length of `model_output`.
- Use a stricter, non-greedy pattern (avoid matching across extraneous nesting).
- Prefer `re.finditer()` and enforce a length constraint on each match.

---

#### 3. vllm/entrypoints/openai/serving_chat.py [Line 351](https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/entrypoints/openai/serving_chat.py#L351)

https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/vllm/entrypoints/openai/serving_chat.py#L351

**Risk Description:**
- The regex `r'.*"parameters":\s*(.*)'` can trigger backtracking if `current_text` is very long and contains repeated structures.
- Especially when processing strings from unknown sources, `.*` matching any content is high risk.

**Remediation Suggestions:**
- Use a more specific pattern (e.g., via JSON parsing).
- Impose limits on `current_text` length.
- Avoid using `.*` to capture large blocks of text; prefer structured parsing when possible.

---

#### 4. benchmarks/benchmark_serving_structured_output.py [Line 650](https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/benchmarks/benchmark_serving_structured_output.py#L650)

https://github.com/vllm-project/vllm/blob/2858830c39da0ae153bc1328dbba7680f5fbebe1/benchmarks/benchmark_serving_structured_output.py#L650

**Risk Description:**
- The regex `r'\{.*\}'` is used to extract JSON inside curly braces. If the `actual` string is very long with unbalanced braces, it can cause backtracking, leading to a ReDoS vulnerability.
- Although this is used for benchmark correctness checking, it should still handle abnormal inputs carefully.

**Remediation Suggestions:**
- Limit the length of `actual`.
- Prefer stepwise search for `{` and `}` or use a robust JSON extraction tool.
- Recommend first locating the range with simple string search, then applying regex.

### Fix

* https://github.com/vllm-project/vllm/pull/18454

---

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-j828-28rj-hfhp
- https://github.com/vllm-project/vllm/pull/18454
- https://github.com/vllm-project/vllm/commit/4fc1bf813ad80172c1db31264beaef7d93fe0601
- https://github.com/vllm-project/vllm

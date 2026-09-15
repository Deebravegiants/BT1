# [M] vLLM: Quadratic Time Complexity in Input Token Processing​ leads to denial of service

## Summary
Severity: Medium
Advisory: GHSA-vc6m-hm49-g9qg
CVE: CVE-2025-46560
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-vc6m-hm49-g9qg
Type: github-advisory

## Affected
- PyPI: `vllm` — affected >=0.8.0 <0.8.5

## Details
### Summary
A critical performance vulnerability has been identified in the input preprocessing logic of the multimodal tokenizer. The code dynamically replaces placeholder tokens (e.g., <|audio_*|>, <|image_*|>) with repeated tokens based on precomputed lengths. Due to ​​inefficient list concatenation operations​​, the algorithm exhibits ​​quadratic time complexity (O(n²))​​, allowing malicious actors to trigger resource exhaustion via specially crafted inputs.

### Details
​​Affected Component​​: input_processor_for_phi4mm function.
https://github.com/vllm-project/vllm/blob/8cac35ba435906fb7eb07e44fe1a8c26e8744f4e/vllm/model_executor/models/phi4mm.py#L1182-L1197

The code modifies the input_ids list in-place using input_ids = input_ids[:i] + tokens + input_ids[i+1:]. Each concatenation operation copies the entire list, leading to O(n) operations per replacement. For k placeholders expanding to m tokens, total time becomes O(kmn), approximating O(n²) in worst-case scenarios.

### PoC
Test data demonstrates exponential time growth:
```python
test_cases = [100, 200, 400, 800, 1600, 3200, 6400]
run_times = [0.002, 0.007, 0.028, 0.136, 0.616, 2.707, 11.854]  # seconds
```
Doubling input size increases runtime by ~4x (consistent with O(n²)).

### Impact
​​Denial-of-Service (DoS):​​ An attacker could submit inputs with many placeholders (e.g., 10,000 <|audio_1|> tokens), causing CPU/memory exhaustion.
Example: 10,000 placeholders → ~100 million operations.


### Remediation Recommendations​
Precompute all placeholder positions and expansion lengths upfront.
Replace dynamic list concatenation with a single preallocated array.
```python
# Pseudocode for O(n) solution
new_input_ids = []
for token in input_ids:
    if token is placeholder:
        new_input_ids.extend([token] * precomputed_length)
    else:
        new_input_ids.append(token)
```

## References
- https://github.com/vllm-project/vllm/security/advisories/GHSA-vc6m-hm49-g9qg
- https://nvd.nist.gov/vuln/detail/CVE-2025-46560
- https://github.com/advisories/GHSA-vc6m-hm49-g9qg
- https://github.com/pypa/advisory-database/tree/main/vulns/vllm/PYSEC-2026-2022.yaml
- https://github.com/vllm-project/vllm
- https://github.com/vllm-project/vllm/blob/8cac35ba435906fb7eb07e44fe1a8c26e8744f4e/vllm/model_executor/models/phi4mm.py#L1182-L1197
- https://pypi.org/project/vllm

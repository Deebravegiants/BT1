# [M] Hugging Face Transformers Regular Expression Denial of Service (ReDoS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9356-575x-2w9m
CVE: CVE-2025-5197
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-06
Source: https://github.com/advisories/GHSA-9356-575x-2w9m
Type: github-advisory

## Affected
- PyPI: `transformers` — affected >=0 <4.53.0

## Details
A Regular Expression Denial of Service (ReDoS) vulnerability exists in the Hugging Face Transformers library, specifically in the `convert_tf_weight_name_to_pt_weight_name()` function. This function, responsible for converting TensorFlow weight names to PyTorch format, uses a regex pattern `/[^/]*___([^/]*)/` that can be exploited to cause excessive CPU consumption through crafted input strings due to catastrophic backtracking. The vulnerability affects versions up to 4.51.3 and is fixed in version 4.53.0. This issue can lead to service disruption, resource exhaustion, and potential API service vulnerabilities, impacting model conversion processes between TensorFlow and PyTorch formats.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5197
- https://github.com/huggingface/transformers/commit/701caef704e356dc2f9331cc3fd5df0eccb4720a
- https://github.com/huggingface/transformers/commit/944b56000be5e9b61af8301aa340838770ad8a0b
- https://github.com/huggingface/transformers
- https://huntr.com/bounties/3f8b3fd0-166b-46e7-b60f-60dd9d2678bf

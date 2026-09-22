# [M] Xinference 3.3.0 Unauthenticated Arbitrary-Path File Read via /v1/models/llm/auto-register

## Summary
Severity: Medium
Advisory: CVE-2026-85668
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85668
Type: osv

## Details
Xinference (affected commit 4a94832, v3.x) contains an unauthenticated arbitrary-path file read vulnerability in the POST /v1/models/llm/auto-register endpoint, which accepts a caller-supplied model_path parameter without authentication or path confinement. The endpoint reads and parses config.json, tokenizer_config.json, and chat_template.jinja files at the supplied path and reflects the parsed content back to the caller, allowing an unauthenticated attacker to probe the server filesystem and extract content of files with those names in any directory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85668.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85668
- https://www.vulncheck.com/advisories/xinference-3.3.0-unauthenticated-arbitrary-path-file-read-via-v1-models-llm-auto-register
- https://github.com/xorbitsai/inference/issues/5176
- https://github.com/xorbitsai/inference
- https://github.com/xorbitsai/inference/blob/v3.3.0/xinference/model/llm/config_parser.py

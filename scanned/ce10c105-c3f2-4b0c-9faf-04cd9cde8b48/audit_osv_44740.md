# [H] FastChat Unauthenticated Worker Registration SSRF and Model Spoofing

## Summary
Severity: High
Advisory: CVE-2026-85695
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85695
Type: osv

## Details
FastChat contains an authentication bypass vulnerability in the /register_worker endpoint that allows unauthenticated attackers to register arbitrary worker addresses and perform server-side request forgery. Attackers can register malicious workers under victim model names to intercept user prompts, images, and responses, or probe internal network ports across the worker mesh.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85695.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85695
- https://www.vulncheck.com/advisories/fastchat-unauthenticated-worker-registration-ssrf-and-model-spoofing
- https://github.com/lm-sys/FastChat/issues/3886
- https://github.com/lm-sys/FastChat
- https://github.com/lm-sys/FastChat/blob/v0.2.36/fastchat/serve/controller.py

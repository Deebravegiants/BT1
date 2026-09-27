# [H] Remote Code Execution in infiniflow/ragflow

## Summary
Severity: High
Advisory: CVE-2024-10131
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-19
Source: https://osv.dev/vulnerability/CVE-2024-10131
Type: osv

## Details
The `add_llm` function in `llm_app.py` in infiniflow/ragflow version 0.11.0 contains a remote code execution (RCE) vulnerability. The function uses user-supplied input `req['llm_factory']` and `req['llm_name']` to dynamically instantiate classes from various model dictionaries. This approach allows an attacker to potentially execute arbitrary code due to the lack of comprehensive input validation or sanitization. An attacker could provide a malicious value for 'llm_factory' that, when used as an index to these model dictionaries, results in the execution of arbitrary code.

## References
- https://huntr.com/bounties/42ae0b27-e851-4b58-a991-f691a437fbaa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10131.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10131

# [C] Perspective 5.0.0 RCE via eval() Expression Injection

## Summary
Severity: Critical
Advisory: CVE-2026-67195
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-67195
Type: osv

## Details
Perspective 5.0.0 contains a remote code execution vulnerability that allows unauthenticated attackers to execute arbitrary operating system commands by submitting crafted expression strings to the PolarsVirtualServer backend, which passes client-supplied input directly to Python's eval() with only __builtins__={} cleared. Attackers can exploit Python object attribute traversal through the interpreter's loaded class list to reach subprocess.Popen via a TableValidateExprReq or TableMakeViewReq protobuf message, achieving arbitrary command execution in the Perspective host process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67195.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67195
- https://www.vulncheck.com/advisories/perspective-rce-via-eval-expression-injection
- https://github.com/perspective-dev/perspective
- https://christbowel.com/blog/perspective-5-0-0-five-cves/

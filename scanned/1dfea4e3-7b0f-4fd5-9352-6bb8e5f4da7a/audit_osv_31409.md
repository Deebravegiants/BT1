# [H] Server-Side Template Injection (SSTI) in significant-gravitas/autogpt

## Summary
Severity: High
Advisory: CVE-2025-1040
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2025-1040
Type: osv

## Details
AutoGPT versions 0.3.4 and earlier are vulnerable to a Server-Side Template Injection (SSTI) that could lead to Remote Code Execution (RCE). The vulnerability arises from the improper handling of user-supplied format strings in the `AgentOutputBlock` implementation, where malicious input is passed to the Jinja2 templating engine without adequate security measures. Attackers can exploit this flaw to execute arbitrary commands on the host system. The issue is fixed in version 0.4.0.

## References
- https://huntr.com/bounties/b74ef75f-61d5-4422-ab15-9550c8b4f185
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1040.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-1040
- https://github.com/significant-gravitas/autogpt/commit/6dba31e0215549604bdcc1aed24e3a1714e75ee2

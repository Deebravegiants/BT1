# [H] CVE-2026-24222

## Summary
Severity: High
Advisory: CVE-2026-24222
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/CVE-2026-24222
Type: osv

## Details
NVIDIA NeMoClaw contains a vulnerability in the sandbox environment initialization component, where a remote attacker could cause improper access control by sending prompt-injected content that causes the agent to read and exfiltrate host environment variables not properly restricted during sandbox creation. A successful exploit of this vulnerability might lead to information disclosure.

## References
- https://nvidia.custhelp.com/app/answers/detail/a_id/5837
- https://www.cve.org/CVERecord?id=CVE-2026-24222
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24222.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24222

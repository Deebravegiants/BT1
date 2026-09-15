# [H] Exim Improper Neutralization of Special Elements Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-42117
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-42117
Type: osv

## Details
Exim Improper Neutralization of Special Elements Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Exim. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the smtp service, which listens on TCP port 25 by default. The issue results from the lack of proper validation of user-supplied data, which can result in a memory corruption condition. An attacker can leverage this vulnerability to execute code in the context of the current process. Was ZDI-CAN-17554.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00029.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42117.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42117
- https://www.zerodayinitiative.com/advisories/ZDI-23-1471/

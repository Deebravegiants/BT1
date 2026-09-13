# [H] Exim SMTP Challenge Stack-based Buffer Overflow Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2023-42116
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-03
Source: https://osv.dev/vulnerability/CVE-2023-42116
Type: osv

## Details
Exim SMTP Challenge Stack-based Buffer Overflow Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Exim. Authentication is not required to exploit this vulnerability.

The specific flaw exists within the handling of NTLM challenge requests. The issue results from the lack of proper validation of the length of user-supplied data prior to copying it to a fixed-length stack-based buffer. An attacker can leverage this vulnerability to execute code in the context of the service account.
. Was ZDI-CAN-17515.

## References
- https://lists.debian.org/debian-lts-announce/2023/10/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42116.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-42116
- https://www.zerodayinitiative.com/advisories/ZDI-23-1470/

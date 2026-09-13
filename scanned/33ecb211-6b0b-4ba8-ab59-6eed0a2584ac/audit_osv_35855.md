# [H] Adminer multi_query Incorrect Check of Function Return Value Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-15686
Aliases: GHSA-3582-q6xq-5vf7
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-15686
Type: osv

## Details
Adminer multi_query Incorrect Check of Function Return Value Remote Code Execution Vulnerability. This vulnerability allows remote attackers to execute arbitrary code on affected installations of Adminer. Authentication is required to exploit this vulnerability.

The specific flaw exists within the multi_query method. The issue results from an incorrect check of a function return value. An attacker can leverage this vulnerability to execute code in the context of the web server. Was ZDI-CAN-28201.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15686.json
- https://github.com/vrana/adminer/security/advisories/GHSA-3582-q6xq-5vf7#event-826206
- https://nvd.nist.gov/vuln/detail/CVE-2026-15686
- https://www.zerodayinitiative.com/advisories/ZDI-26-478/

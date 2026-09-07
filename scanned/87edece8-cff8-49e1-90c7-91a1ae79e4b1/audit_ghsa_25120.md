# [M] Yab Quarx persistent cross-site scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-h4fh-gpvh-753g
CVE: CVE-2018-7274
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h4fh-gpvh-753g
Type: github-advisory

## Affected
- Packagist: `yab/quarx` — affected >=0 <2.4.5

## Details
Yab Quarx before 2.4.5 is prone to multiple persistent cross-site scripting vulnerabilities: Blog (Title), FAQ (Question), Pages (Title), Widgets (Name), and Menus (Name).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7274
- https://github.com/GrafiteInc/CMS/issues/115
- https://github.com/YABhq/Quarx/issues/116
- https://github.com/GrafiteInc/CMS/commit/dcc1a5ac3c6d48afd3b8b9d8b11a9c6bfeb75f77
- https://github.com/GrafiteInc/CMS
- http://seclists.org/bugtraq/2018/Feb/53
- http://www.securityfocus.com/bid/103081

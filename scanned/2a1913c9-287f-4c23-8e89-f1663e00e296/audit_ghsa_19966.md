# [M] collective.contact.widget is vulnerable to cross-site scripting 

## Summary
Severity: Medium
Advisory: GHSA-5pqf-rvm7-3wgw
CVE: CVE-2022-4638
CWE: CWE-707, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-5pqf-rvm7-3wgw
Type: github-advisory

## Affected
- PyPI: `collective.contact.widget` — affected >=0 <1.13

## Details
collective.contact.widget is an add-on is part of the collective.contact.* suite. A vulnerability classified as problematic was found in collective.contact.widget up to 1.12. This vulnerability affects the function title of the file src/collective/contact/widget/widgets.py. The manipulation leads to cross site scripting. The attack can be initiated remotely. The name of the patch is 5da36305ca7ed433782be8901c47387406fcda12. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-216496.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4638
- https://github.com/collective/collective.contact.widget/commit/5da36305ca7ed433782be8901c47387406fcda12
- https://github.com/collective/collective.contact.widget
- https://github.com/pypa/advisory-database/tree/main/vulns/collective-contact-widget/PYSEC-2022-42988.yaml
- https://vuldb.com/?id.216496

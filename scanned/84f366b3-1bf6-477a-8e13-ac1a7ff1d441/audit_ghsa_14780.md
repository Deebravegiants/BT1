# [H] ebookmeta XML External Entity vulnerability

## Summary
Severity: High
Advisory: GHSA-hx54-pf28-7xch
CVE: CVE-2024-37388
CWE: CWE-611, CWE-776
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-hx54-pf28-7xch
Type: github-advisory

## Affected
- PyPI: `ebookmeta` — affected >=0 <1.2.8

## Details
An XML External Entity (XXE) vulnerability in the `ebookmeta.get_metadata` function via lxml dependency allows attackers to access sensitive information or cause a Denial of Service (DoS) via crafted XML input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37388
- https://github.com/dnkorpushov/ebookmeta/issues/16#issue-2317712335
- https://github.com/dnkorpushov/ebookmeta

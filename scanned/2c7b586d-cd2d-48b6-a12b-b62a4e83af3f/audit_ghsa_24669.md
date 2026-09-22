# [C] Plone Arbitrary Code Execution via Unsafe Handling of Pickles

## Summary
Severity: Critical
Advisory: GHSA-hf26-vvmx-x8c8
CVE: CVE-2007-5741
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-hf26-vvmx-x8c8
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=2.5 <2.5.5
- PyPI: `Plone` — affected >=3.0 <3.0.3

## Details
Plone 2.5 through 2.5.4 and 3.0 through 3.0.2 allows remote attackers to execute arbitrary Python code via network data containing pickled objects for the (1) statusmessages or (2) linkintegrity module, which the module unpickles and executes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2007-5741
- https://exchange.xforce.ibmcloud.com/vulnerabilities/38288
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2007-4.yaml
- https://web.archive.org/web/20080507055819/https://plone.org/about/security/advisories/cve-2007-5741
- https://web.archive.org/web/20080517012557/http://www.securityfocus.com/bid/26354
- https://web.archive.org/web/20080906150436/http://www.securityfocus.com/archive/1/483343/100/0/threaded
- http://plone.org/about/security/advisories/cve-2007-5741
- http://www.debian.org/security/2007/dsa-1405

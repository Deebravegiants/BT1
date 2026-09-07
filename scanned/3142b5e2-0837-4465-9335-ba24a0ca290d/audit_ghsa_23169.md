# [M] Galaxy cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-qqr6-vm23-m488
CVE: CVE-2018-1000516
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qqr6-vm23-m488
Type: github-advisory

## Affected
- PyPI: `galaxy-app` — affected >=0 <14.10.1
- PyPI: `galaxy-app` — affected >=15.0 <15.01

## Details
The Galaxy Project Galaxy version v14.10 contains a CWE-79: Improper Neutralization of Input During Web Page Generation vulnerability in Many templates used in the Galaxy server did not properly sanitize user's input, which would allow for cross-site scripting (XSS) attacks. In this form of attack, a malicious person can create a URL which, when opened by a Galaxy user or administrator, would allow the malicious user to execute arbitrary Javascript. that can result in Arbitrary JavaScript code execution. This attack appear to be exploitable via The victim must interact with component on page witch contains injected JavaScript code.. This vulnerability appears to have been fixed in v14.10.1, v15.01.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000516
- https://galaxyproject.org/archive/dev-news-briefs/2015-01-13/#security
- https://github.com/galaxyproject/galaxy
- https://github.com/pypa/advisory-database/tree/main/vulns/galaxy-app/PYSEC-2018-149.yaml

# [C] Incorrect Permission Assignment for Critical Resource	in Plone

## Summary
Severity: Critical
Advisory: GHSA-hm2p-fhwx-9285
CVE: CVE-2021-33509
CWE: CWE-732
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-15
Source: https://github.com/advisories/GHSA-hm2p-fhwx-9285
Type: github-advisory

## Affected
- PyPI: `Plone` — affected >=0 <5.2.5

## Details
Plone through 5.2.4 allows remote authenticated managers to perform disk I/O via crafted keyword arguments to the ReStructuredText transform in a Python script.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33509
- https://github.com/advisories/GHSA-hm2p-fhwx-9285
- https://github.com/plone/Plone
- https://github.com/pypa/advisory-database/tree/main/vulns/plone/PYSEC-2021-81.yaml
- https://plone.org/security/hotfix/20210518/writing-arbitrary-files-via-docutils-and-python-script
- http://www.openwall.com/lists/oss-security/2021/05/22/1

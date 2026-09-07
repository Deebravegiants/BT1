# [M] Cross-site scripting in papermerge

## Summary
Severity: Medium
Advisory: GHSA-9w49-m7xh-5r39
CVE: CVE-2020-29456
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-20
Source: https://github.com/advisories/GHSA-9w49-m7xh-5r39
Type: github-advisory

## Affected
- PyPI: `papermerge` — affected >=1.2.0 <1.5.2

## Details
Multiple cross-site scripting (XSS) vulnerabilities in Papermerge before 1.5.2 allow remote attackers to inject arbitrary web script or HTML via the rename, tag, upload, or create folder function. The payload can be in a folder, a tag, or a document's filename. If email consumption is configured in Papermerge, a malicious document can be sent by email and is automatically uploaded into the Papermerge web application. Therefore, no authentication is required to exploit XSS if email consumption is configured. Otherwise authentication is required.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29456
- https://github.com/ciur/papermerge/issues/228
- https://github.com/advisories/GHSA-9w49-m7xh-5r39
- https://github.com/ciur/papermerge
- https://github.com/ciur/papermerge/releases/tag/v1.5.2
- https://github.com/pypa/advisory-database/tree/main/vulns/papermerge/PYSEC-2020-74.yaml
- https://www.papermerge.com

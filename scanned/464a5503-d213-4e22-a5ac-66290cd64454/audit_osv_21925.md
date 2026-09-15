# [H] URL Restriction Bypass in plantuml/plantuml

## Summary
Severity: High
Advisory: CVE-2022-1379
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N)
Published: 2022-05-14
Source: https://osv.dev/vulnerability/CVE-2022-1379
Type: osv

## Details
URL Restriction Bypass in GitHub repository plantuml/plantuml prior to V1.2022.5. An attacker can abuse this to bypass URL restrictions that are imposed by the different security profiles and achieve server side request forgery (SSRF). This allows accessing restricted internal resources/servers or sending requests to third party servers.

## References
- https://huntr.dev/bounties/0d737527-86e1-41d1-9d37-b2de36bc063a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1379.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CHUE4G5CAJUD7L2QPJF6U4JYQTP7CNNL/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J4DP36G2VBOZUNQIUZ5LVJKZIVO4SDAI/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1379
- https://github.com/plantuml/plantuml/commit/93e5964e5f35914f3f7b89de620c596795550083

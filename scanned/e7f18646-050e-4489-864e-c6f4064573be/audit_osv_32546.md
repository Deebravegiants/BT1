# [M] Unexpected external content may be displayed in DNN ImageHandler

## Summary
Severity: Medium
Advisory: CVE-2025-32371
Aliases: GHSA-2rrc-g594-rhqw
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2025-04-09
Source: https://osv.dev/vulnerability/CVE-2025-32371
Type: osv

## Details
DNN (formerly DotNetNuke) is an open-source web content management platform (CMS) in the Microsoft ecosystem. A url could be crafted to the DNN ImageHandler to render text from a querystring parameter. This text would display in the resulting image and a user that trusts the domain might think that the information is legitimate. This vulnerability is fixed in 9.13.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32371.json
- https://github.com/dnnsoftware/Dnn.Platform/security/advisories/GHSA-2rrc-g594-rhqw
- https://nvd.nist.gov/vuln/detail/CVE-2025-32371
- https://github.com/dnnsoftware/Dnn.Platform/commit/5def7cc2e7931bb1041b21540bde99f96874a5a9

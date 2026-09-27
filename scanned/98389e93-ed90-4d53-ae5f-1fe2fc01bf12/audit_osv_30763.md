# [C] Remote code execution in onyxia-api

## Summary
Severity: Critical
Advisory: CVE-2024-56333
Aliases: GHSA-qmcw-h4f9-j3h3
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2024-12-20
Source: https://osv.dev/vulnerability/CVE-2024-56333
Type: osv

## Details
Onyxia is a web app that aims at being the glue between multiple open source backend technologies to provide a state of art working environment for data scientists. This critical vulnerability allows authenticated users to remotely execute code within the Onyxia-API, leading to potential consequences such as unauthorized access to other user environments and denial of service attacks. This issue has been patched in api versions 4.2.0, 3.1.1, and 2.8.2. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://docs.onyxia.sh/vulnerability-disclosure/known-vulnerabilities/vulnerability-20241219
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56333.json
- https://github.com/InseeFrLab/onyxia/security/advisories/GHSA-qmcw-h4f9-j3h3
- https://nvd.nist.gov/vuln/detail/CVE-2024-56333

# [M] Element Web vulnerable to potential exposure of access token via authenticated media

## Summary
Severity: Medium
Advisory: CVE-2024-47779
Aliases: GHSA-3jm3-x98c-r34x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-47779
Type: osv

## Details
Element is a Matrix web client built using the Matrix React SDK. Element Web versions 1.11.70 through 1.11.80 contain a vulnerability which can, under specially crafted conditions, lead to the access token becoming exposed to third parties. At least one vector has been identified internally, involving malicious widgets, but other vectors may exist. Note that despite superficial similarity to CVE-2024-47771, this is an entirely separate vulnerability, caused by a separate piece of code included only in Element Web. Element Web and Element Desktop share most but not all, of their code and this vulnerability exists in the part of the code base which is not shared between the projects. Users are strongly advised to upgrade to version 1.11.81 to remediate the issue. As a workaround, avoid granting permissions to untrusted widgets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47779.json
- https://github.com/element-hq/element-web/security/advisories/GHSA-3jm3-x98c-r34x
- https://nvd.nist.gov/vuln/detail/CVE-2024-47779
- https://github.com/element-hq/element-web/commit/8d7f2b5c1301129a488d3597f3839bd74203ee62

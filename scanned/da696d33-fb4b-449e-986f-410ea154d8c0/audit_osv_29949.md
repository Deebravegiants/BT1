# [M] Element Desktop vulnerable to potential exposure of access token via authenticated media

## Summary
Severity: Medium
Advisory: CVE-2024-47771
Aliases: GHSA-963w-49j9-gxj6
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-47771
Type: osv

## Details
Element Desktop is a Matrix client for desktop platforms. Element Desktop versions 1.11.70 through 1.11.80 contain a vulnerability which can, under specially crafted conditions, lead to the access token becoming exposed to third parties. At least one vector has been identified internally, involving malicious widgets, but other vectors may exist. Users are strongly advised to upgrade to version 1.11.81 to remediate the issue. As a workaround, avoid granting permissions to untrusted widgets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47771.json
- https://github.com/element-hq/element-desktop/security/advisories/GHSA-963w-49j9-gxj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-47771
- https://github.com/element-hq/element-desktop/commit/6c78684e84ba7f460aedba6f017760e2323fdf4b
- https://github.com/element-hq/element-web/commit/63c8550791a0221189f495d6458fee7db601c789

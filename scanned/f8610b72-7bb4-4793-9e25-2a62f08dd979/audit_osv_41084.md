# [M] CyberChef: Prototype pollution in Series Chart operation

## Summary
Severity: Medium
Advisory: CVE-2026-57439
Aliases: GHSA-fx6f-382r-j72c
CVSS: 5.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-57439
Type: osv

## Details
CyberChef is a web app for encryption, encoding, compression, and data analysis. Prior to 11.2.0, the Series Chart operation accepts __proto__ as a key while parsing user-supplied CSV, allowing prototype pollution that can be chained with operations such as Parse UDP to inject malicious JavaScript into HTML output. This issue is fixed in version 11.2.0.

## References
- https://github.com/gchq/CyberChef/releases/tag/v11.2.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57439.json
- https://github.com/gchq/CyberChef/security/advisories/GHSA-fx6f-382r-j72c
- https://nvd.nist.gov/vuln/detail/CVE-2026-57439
- https://github.com/gchq/CyberChef/issues/2568
- https://github.com/gchq/CyberChef/commit/85db3be5d0096859b810f0e8d3e151d5dc9b948f
- https://github.com/gchq/CyberChef/pull/2569

# [M] php-svg-lib possible DoS caused by infinite recursion when parsing SVG document

## Summary
Severity: Medium
Advisory: CVE-2023-50251
Aliases: GHSA-ff5x-7qg5-vwf2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-50251
Type: osv

## Details
php-svg-lib is an SVG file parsing / rendering library. Prior to version 0.5.1, when parsing the attributes passed to a `use` tag inside an svg document, an attacker can cause the system to go to an infinite recursion. Depending on the system configuration and attack pattern this could exhaust the memory available to the executing process and/or to the server itself. An attacker sending multiple request to a system to render the above payload can potentially cause resource exhaustion to the point that the system is unable to handle incoming request. Version 0.5.1 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50251.json
- https://github.com/dompdf/php-svg-lib/security/advisories/GHSA-ff5x-7qg5-vwf2
- https://nvd.nist.gov/vuln/detail/CVE-2023-50251
- https://github.com/dompdf/php-svg-lib/commit/88163cbe562d9b391b3a352e54d9c89d02d77ee0

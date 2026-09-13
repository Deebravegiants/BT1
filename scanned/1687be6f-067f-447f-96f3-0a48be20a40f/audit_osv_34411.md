# [C] MapServer - WFS XML Filter Query SQL injection

## Summary
Severity: Critical
Advisory: CVE-2025-59431
Aliases: GHSA-256m-rx4h-r55w
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-59431
Type: osv

## Details
MapServer is a system for developing web-based GIS applications. Prior to 8.4.1, the XML Filter Query directive PropertyName is vulnerably to Boolean-based SQL injection. It seems like expression checking is bypassed by introducing double quote characters in the PropertyName. Allowing to manipulate backend database queries. This vulnerability is fixed in 8.4.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59431.json
- https://github.com/MapServer/MapServer/security/advisories/GHSA-256m-rx4h-r55w
- https://nvd.nist.gov/vuln/detail/CVE-2025-59431

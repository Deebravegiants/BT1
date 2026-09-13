# [M] Frappe Learning Holds Potential for Malicious SVG Upload in Image Upload Feature

## Summary
Severity: Medium
Advisory: CVE-2025-55006
Aliases: CVE-2025-11282, GHSA-mvxw-r9x4-3vrr
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-08-09
Source: https://osv.dev/vulnerability/CVE-2025-55006
Type: osv

## Details
Frappe Learning is a learning system that helps users structure their content. In versions 2.33.0 and below, the image upload functionality did not adequately sanitize uploaded SVG files. This allowed users to upload SVG files containing embedded JavaScript or other potentially malicious content. Malicious SVG files could be used to execute arbitrary scripts in the context of other users. A fix for this issue is planned for version 2.34.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55006.json
- https://github.com/frappe/lms/security/advisories/GHSA-mvxw-r9x4-3vrr
- https://nvd.nist.gov/vuln/detail/CVE-2025-55006

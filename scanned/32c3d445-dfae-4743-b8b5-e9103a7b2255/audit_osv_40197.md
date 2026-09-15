# [M] CVE-2026-50745

## Summary
Severity: Medium
Advisory: CVE-2026-50745
CVSS: 4.7 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-50745
Type: osv

## Details
A missing sanitisation vulnerability exists with user input in the stats-video.php script. The way URLs to this script were constructed did not follow best practices, and the output of the Smarty custom helper function url was neither properly encoded nor sanitised, allowing user‑supplied input to be reflected without escaping.

## References
- https://hackerone.com/reports/3793243
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50745.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50745

# [H] CVE-2018-1265

## Summary
Severity: High
Advisory: CVE-2018-1265
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-06
Source: https://osv.dev/vulnerability/CVE-2018-1265
Type: osv

## Details
Cloud Foundry Diego, release versions prior to 2.8.0, does not properly sanitize file paths in tar and zip files headers. A remote attacker with CF admin privileges can upload a malicious buildpack that will allow a complete takeover of a Diego Cell VM and access to all apps running on that Diego Cell.

## References
- https://www.cloudfoundry.org/blog/cve-2018-1265/

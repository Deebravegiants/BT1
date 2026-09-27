# [M] CVE-2019-3784

## Summary
Severity: Medium
Advisory: CVE-2019-3784
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-03-07
Source: https://osv.dev/vulnerability/CVE-2019-3784
Type: osv

## Details
Cloud Foundry Stratos, versions prior to 2.3.0, contains an insecure session that can be spoofed. When deployed on cloud foundry with multiple instances using the default embedded SQLite database, a remote authenticated malicious user can switch sessions to another user with the same session id.

## References
- https://www.cloudfoundry.org/blog/cve-2019-3784

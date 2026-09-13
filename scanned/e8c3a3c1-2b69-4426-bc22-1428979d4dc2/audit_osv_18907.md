# [M] CVE-2020-37248

## Summary
Severity: Medium
Advisory: CVE-2020-37248
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2020-37248
Type: osv

## Details
OfflineIMAP before 8.0.3 trusts the server with their STARTTLS capability prior to authentication, which allows STRIPTLS/man-in-the-middle attacks, taking over the connection and extracting account credentials in cleartext.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/3
- https://github.com/OfflineIMAP/offlineimap/issues/669
- https://github.com/OfflineIMAP/offlineimap3/issues/222
- https://github.com/OfflineIMAP/offlineimap3/commit/46505c53ef995455d66c685f9ec3ff6ea93dbb74
- https://pypi.org/project/offlineimap/#history

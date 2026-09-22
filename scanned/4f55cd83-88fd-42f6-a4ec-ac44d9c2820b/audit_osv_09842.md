# [H] CVE-2017-11667

## Summary
Severity: High
Advisory: CVE-2017-11667
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-07-26
Source: https://osv.dev/vulnerability/CVE-2017-11667
Type: osv

## Details
OpenProject before 6.1.6 and 7.x before 7.0.3 mishandles session expiry, which allows remote attackers to perform APIv3 requests indefinitely by leveraging a hijacked session.

## References
- https://www.openproject.org/openproject-6-1-6-released-security-fix/
- https://www.openproject.org/openproject-7-0-3-released/
- https://github.com/opf/openproject/commit/0fdd7578909d2ec50abc275fc4962e99566437ee

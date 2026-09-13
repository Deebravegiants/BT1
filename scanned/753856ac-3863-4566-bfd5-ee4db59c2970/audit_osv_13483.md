# [C] CVE-2018-19991

## Summary
Severity: Critical
Advisory: CVE-2018-19991
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-19991
Type: osv

## Details
VeryNginx 0.3.3 allows remote attackers to bypass the Web Application Firewall feature because there is no error handler (for get_uri_args or get_post_args) to block the API misuse described in CVE-2018-9230.

## References
- https://github.com/alexazhou/VeryNginx/issues/218

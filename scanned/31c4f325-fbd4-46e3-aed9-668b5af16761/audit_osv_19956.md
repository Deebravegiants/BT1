# [H] CVE-2021-28379

## Summary
Severity: High
Advisory: CVE-2021-28379
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-28379
Type: osv

## Details
web/upload/UploadHandler.php in Vesta Control Panel (aka VestaCP) through 0.9.8-27 and myVesta through 0.9.8-26-39 allows uploads from a different origin.

## References
- https://github.com/myvesta/vesta/commit/3402071e950e76b79fa8672a1e09b70d3860f355
- http://packetstormsecurity.com/files/161836/VestaCP-0.9.8-Cross-Site-Request-Forgery.html

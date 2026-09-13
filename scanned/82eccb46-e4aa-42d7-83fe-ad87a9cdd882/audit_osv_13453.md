# [H] CVE-2018-19960

## Summary
Severity: High
Advisory: CVE-2018-19960
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-07
Source: https://osv.dev/vulnerability/CVE-2018-19960
Type: osv

## Details
The debug_mode function in web/web.py in OnionShare through 1.3.1, when --debug is enabled, uses the /tmp/onionshare_server.log pathname for logging, which might allow local users to overwrite files or obtain sensitive information by using this pathname.

## References
- https://bugs.debian.org/915859

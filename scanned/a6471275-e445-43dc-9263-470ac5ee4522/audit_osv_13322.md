# [M] CVE-2018-19217

## Summary
Severity: Medium
Advisory: CVE-2018-19217
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19217
Type: osv

## Details
In ncurses, possibly a 6.x version, there is a NULL pointer dereference at the function _nc_name_match that will lead to a denial of service attack. NOTE: the original report stated version 6.1, but the issue did not reproduce for that version according to the maintainer or a reliable third-party

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1643753

# [M] CVE-2018-19757

## Summary
Severity: Medium
Advisory: CVE-2018-19757
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-30
Source: https://osv.dev/vulnerability/CVE-2018-19757
Type: osv

## Details
There is a NULL pointer dereference at function sixel_helper_set_additional_message (status.c) in libsixel 1.8.2 that will cause a denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1649197

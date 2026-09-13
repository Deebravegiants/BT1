# [M] CVE-2021-4214

## Summary
Severity: Medium
Advisory: CVE-2021-4214
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4214
Type: osv

## Details
A heap overflow flaw was found in libpngs' pngimage.c program. This flaw allows an attacker with local network access to pass a specially crafted PNG file to the pngimage utility, causing an application to crash, leading to a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2021-4214
- https://security-tracker.debian.org/tracker/CVE-2021-4214
- https://security.netapp.com/advisory/ntap-20221020-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2043393
- https://github.com/glennrp/libpng/issues/302

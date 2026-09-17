# [M] CVE-2020-21049

## Summary
Severity: Medium
Advisory: CVE-2020-21049
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-14
Source: https://osv.dev/vulnerability/CVE-2020-21049
Type: osv

## Details
An invalid read in the stb_image.h component of libsixel prior to v1.8.5 allows attackers to cause a denial of service (DOS) via a crafted PSD file.

## References
- https://github.com/saitoha/libsixel/blob/master/ChangeLog
- https://github.com/saitoha/libsixel/releases/tag/v1.8.5
- https://bitbucket.org/netbsd/pkgsrc/commits/970a81d31ec7498e04d09b6b7771cef35f63cd28
- https://github.com/saitoha/libsixel/commit/0b1e0b3f7b44233f84e5c9f512f8c90d6bbbe33d
- https://github.com/saitoha/libsixel/issues/74

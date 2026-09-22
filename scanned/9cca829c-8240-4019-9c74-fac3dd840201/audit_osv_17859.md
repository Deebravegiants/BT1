# [M] CVE-2020-21048

## Summary
Severity: Medium
Advisory: CVE-2020-21048
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-09-14
Source: https://osv.dev/vulnerability/CVE-2020-21048
Type: osv

## Details
An issue in the dither.c component of libsixel prior to v1.8.4 allows attackers to cause a denial of service (DOS) via a crafted PNG file.

## References
- https://github.com/saitoha/libsixel/blob/master/ChangeLog
- https://github.com/saitoha/libsixel/releases/tag/v1.8.4
- https://bitbucket.org/netbsd/pkgsrc/commits/6f0c011cbfccdffa635d04c84433b1a02687adad
- https://github.com/saitoha/libsixel/commit/cb373ab6614c910407c5e5a93ab935144e62b037
- https://github.com/saitoha/libsixel/issues/73

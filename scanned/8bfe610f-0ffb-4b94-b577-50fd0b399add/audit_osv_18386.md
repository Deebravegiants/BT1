# [M] CVE-2020-26932

## Summary
Severity: Medium
Advisory: CVE-2020-26932
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-10-10
Source: https://osv.dev/vulnerability/CVE-2020-26932
Type: osv

## Details
debian/sympa.postinst for the Debian Sympa package before 6.2.40~dfsg-7 uses mode 4755 for sympa_newaliases-wrapper, whereas the intended permissions are mode 4750 (for access by the sympa group)

## References
- https://bugs.debian.org/971904
- https://salsa.debian.org/sympa-team/sympa/-/merge_requests/1
- https://www.debian.org/security/2020/dsa-4818

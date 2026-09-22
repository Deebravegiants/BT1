# [M] CVE-2019-12875

## Summary
Severity: Medium
Advisory: CVE-2019-12875
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2019-12875
Type: osv

## Details
Alpine Linux abuild through 3.4.0 allows an unprivileged member of the abuild group to add an untrusted package via a --keys-dir option that causes acceptance of an untrusted signing key.

## References
- https://security.netapp.com/advisory/ntap-20190625-0005/
- https://code.foxkit.us/adelie/packages/commit/15b160780c6eeff7048063c099a7f8757e1d8391
- https://github.com/sroracle/abuild/commit/4f90ce92778d0ee302e288def75591b96a397c8b

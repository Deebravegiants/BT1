# [H] CVE-2020-1921

## Summary
Severity: High
Advisory: CVE-2020-1921
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-10
Source: https://osv.dev/vulnerability/CVE-2020-1921
Type: osv

## Details
In the crypt function, we attempt to null terminate a buffer using the size of the input salt without validating that the offset is within the buffer. This issue affects HHVM versions prior to 4.56.3, all versions between 4.57.0 and 4.80.1, all versions between 4.81.0 and 4.93.1, and versions 4.94.0, 4.95.0, 4.96.0, 4.97.0, 4.98.0.

## References
- https://hhvm.com/blog/2021/02/25/security-update.html
- https://github.com/facebook/hhvm/commit/08193b7f0cd3910256e00d599f0f3eb2519c44ca

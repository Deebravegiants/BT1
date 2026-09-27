# [M] CVE-2017-8843

## Summary
Severity: Medium
Advisory: CVE-2017-8843
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-05-08
Source: https://osv.dev/vulnerability/CVE-2017-8843
Type: osv

## Details
The join_pthread function in stream.c in liblrzip.so in lrzip 0.631 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted archive.

## References
- https://blogs.gentoo.org/ago/2017/05/07/lrzip-null-pointer-dereference-in-join_pthread-stream-c/
- https://security.gentoo.org/glsa/202005-01
- https://github.com/ckolivas/lrzip/issues/69

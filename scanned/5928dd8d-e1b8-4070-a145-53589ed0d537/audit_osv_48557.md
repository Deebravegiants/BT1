# [M] CVE-2017-9408

## Summary
Severity: Medium
Advisory: CVE-2017-9408
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-02
Source: https://osv.dev/vulnerability/CVE-2017-9408
Type: osv

## Details
In Poppler 0.54.0, a memory leak vulnerability was found in the function Object::initArray in Object.cc, which allows attackers to cause a denial of service via a crafted file.

## References
- https://security.gentoo.org/glsa/201801-17
- https://www.debian.org/security/2018/dsa-4079
- https://bugs.freedesktop.org/show_bug.cgi?id=100776

# [H] CVE-2016-2194

## Summary
Severity: High
Advisory: CVE-2016-2194
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-13
Source: https://osv.dev/vulnerability/CVE-2016-2194
Type: osv

## Details
The ressol function in Botan before 1.10.11 and 1.11.x before 1.11.27 allows remote attackers to cause a denial of service (infinite loop) via unspecified input to the OS2ECP function, related to a composite modulus.

## References
- http://botan.randombit.net/security.html
- http://marc.info/?l=botan-devel&m=145435148602911&w=2
- http://marc.info/?l=botan-devel&m=145449001708138&w=2
- http://www.debian.org/security/2016/dsa-3565
- https://security.gentoo.org/glsa/201612-38

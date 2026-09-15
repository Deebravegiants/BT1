# [H] CVE-2018-12565

## Summary
Severity: High
Advisory: CVE-2018-12565
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12565
Type: osv

## Details
An issue was discovered in Linaro LAVA before 2018.5.post1. Because of use of yaml.load() instead of yaml.safe_load() when parsing user data, remote code execution can occur.

## References
- https://www.debian.org/security/2018/dsa-4234
- https://git.linaro.org/lava/lava.git/commit/?id=583666c84ea2f12797a3eb71392bcb05782f5b14

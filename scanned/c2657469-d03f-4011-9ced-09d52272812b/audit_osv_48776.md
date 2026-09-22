# [C] CVE-2018-13043

## Summary
Severity: Critical
Advisory: CVE-2018-13043
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-01
Source: https://osv.dev/vulnerability/CVE-2018-13043
Type: osv

## Details
scripts/grep-excuses.pl in Debian devscripts through 2.18.3 allows code execution through unsafe YAML loading because YAML::Syck is used without a configuration that prevents unintended blessing.

## References
- https://usn.ubuntu.com/3704-1/
- https://bugs.debian.org/902409

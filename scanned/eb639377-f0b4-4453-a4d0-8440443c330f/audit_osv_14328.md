# [M] CVE-2018-9058

## Summary
Severity: Medium
Advisory: CVE-2018-9058
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-03-27
Source: https://osv.dev/vulnerability/CVE-2018-9058
Type: osv

## Details
In Long Range Zip (aka lrzip) 0.631, there is an infinite loop in the runzip_fd function of runzip.c. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted lrz file.

## References
- https://github.com/ckolivas/lrzip/issues/93

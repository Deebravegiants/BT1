# [M] CVE-2018-20029

## Summary
Severity: Medium
Advisory: CVE-2018-20029
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-20029
Type: osv

## Details
The nxfs.sys driver in the DokanFS library 0.6.0 in NoMachine before 6.4.6 on Windows 10 allows local users to cause a denial of service (BSOD) because uninitialized memory can be read.

## References
- https://www.nomachine.com/TR11P08975

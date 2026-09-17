# [M] CVE-2020-27819

## Summary
Severity: Medium
Advisory: CVE-2020-27819
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2020-27819
Type: osv

## Details
An issue was discovered in libxls before and including 1.6.1 when reading Microsoft Excel files. A NULL pointer dereference vulnerability exists when parsing XLS cells in libxls/xls2csv.c:199. It could allow a remote attacker to cause a denial of service via crafted XLS file.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1903296

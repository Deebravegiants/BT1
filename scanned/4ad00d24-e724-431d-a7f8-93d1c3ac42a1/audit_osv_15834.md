# [M] CVE-2019-19958

## Summary
Severity: Medium
Advisory: CVE-2019-19958
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19958
Type: osv

## Details
In libIEC61850 1.4.0, StringUtils_createStringFromBuffer in common/string_utilities.c has an integer signedness issue that could lead to an attempted excessive memory allocation and denial of service.

## References
- https://github.com/mz-automation/libiec61850/issues/198

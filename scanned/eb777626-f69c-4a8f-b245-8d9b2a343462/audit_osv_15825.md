# [M] CVE-2019-19930

## Summary
Severity: Medium
Advisory: CVE-2019-19930
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-23
Source: https://osv.dev/vulnerability/CVE-2019-19930
Type: osv

## Details
In libIEC61850 1.4.0, MmsValue_newOctetString in mms/iso_mms/common/mms_value.c has an integer signedness error that can lead to an attempted excessive memory allocation.

## References
- https://github.com/mz-automation/libiec61850/issues/193

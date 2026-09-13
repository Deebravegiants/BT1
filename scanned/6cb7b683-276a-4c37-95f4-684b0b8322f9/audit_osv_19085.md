# [H] CVE-2020-7054

## Summary
Severity: High
Advisory: CVE-2020-7054
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-14
Source: https://osv.dev/vulnerability/CVE-2020-7054
Type: osv

## Details
MmsValue_decodeMmsData in mms/iso_mms/server/mms_access_result.c in libIEC61850 through 1.4.0 has a heap-based buffer overflow when parsing the MMS_BIT_STRING data type.

## References
- https://github.com/mz-automation/libiec61850/issues/200

# [M] CVE-2019-19957

## Summary
Severity: Medium
Advisory: CVE-2019-19957
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-24
Source: https://osv.dev/vulnerability/CVE-2019-19957
Type: osv

## Details
In libIEC61850 1.4.0, getNumberOfElements in mms/iso_mms/server/mms_access_result.c has an out-of-bounds read vulnerability, related to bufPos and elementLength.

## References
- https://github.com/mz-automation/libiec61850/issues/197

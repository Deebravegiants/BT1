# [H] CVE-2021-45769

## Summary
Severity: High
Advisory: CVE-2021-45769
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-14
Source: https://osv.dev/vulnerability/CVE-2021-45769
Type: osv

## Details
A NULL pointer dereference in AcseConnection_parseMessage at src/mms/iso_acse/acse.c of libiec61850 v1.5.0 can lead to a segmentation fault or application crash.

## References
- https://github.com/mz-automation/libiec61850/issues/368

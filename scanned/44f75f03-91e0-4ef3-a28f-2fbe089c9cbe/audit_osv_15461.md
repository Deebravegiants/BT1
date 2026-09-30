# [H] CVE-2019-16510

## Summary
Severity: High
Advisory: CVE-2019-16510
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-16510
Type: osv

## Details
libIEC61850 through 1.3.3 has a use-after-free in MmsServer_waitReady in mms/iso_mms/server/mms_server.c, as demonstrated by server_example_goose.

## References
- https://github.com/mz-automation/libiec61850/issues/164

# [H] CVE-2019-6719

## Summary
Severity: High
Advisory: CVE-2019-6719
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-23
Source: https://osv.dev/vulnerability/CVE-2019-6719
Type: osv

## Details
An issue has been found in libIEC61850 v1.3.1. There is a use-after-free in the getState function in mms/iso_server/iso_server.c, as demonstrated by examples/server_example_goose/server_example_goose.c and examples/server_example_61400_25/server_example_61400_25.c.

## References
- https://github.com/mz-automation/libiec61850/issues/111

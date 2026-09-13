# [H] CVE-2019-6136

## Summary
Severity: High
Advisory: CVE-2019-6136
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-01-11
Source: https://osv.dev/vulnerability/CVE-2019-6136
Type: osv

## Details
An issue has been found in libIEC61850 v1.3.1. Ethernet_setProtocolFilter in hal/ethernet/linux/ethernet_linux.c has a SEGV, as demonstrated by sv_subscriber_example.c and sv_subscriber.c.

## References
- https://github.com/mz-automation/libiec61850/issues/105

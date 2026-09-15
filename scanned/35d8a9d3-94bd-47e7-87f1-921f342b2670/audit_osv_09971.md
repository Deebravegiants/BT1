# [H] CVE-2017-12463

## Summary
Severity: High
Advisory: CVE-2017-12463
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2017-12463
Type: osv

## Details
Memory leak in the ccnl_app_RX function in ccnl-uapi.c in CCN-lite before 2.00 allows context-dependent attackers to cause a denial of service (memory consumption) via vectors involving an envelope_s structure pointer when the packet format is unknown.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/129

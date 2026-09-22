# [H] CVE-2021-36513

## Summary
Severity: High
Advisory: CVE-2021-36513
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-10-18
Source: https://osv.dev/vulnerability/CVE-2021-36513
Type: osv

## Details
An issue was discovered in function sofia_handle_sip_i_notify in sofia.c in SignalWire freeswitch before 1.10.6, may allow attackers to view sensitive information due to an uninitialized value.

## References
- https://github.com/signalwire/freeswitch/releases/tag/v1.10.6
- https://newreleases.io/project/github/signalwire/freeswitch/release/v1.10.6
- https://github.com/signalwire/freeswitch/issues/1245

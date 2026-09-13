# [H] CVE-2018-18838

## Summary
Severity: High
Advisory: CVE-2018-18838
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2018-18838
Type: osv

## Details
An issue was discovered in Netdata 1.10.0. Log Injection (or Log Forgery) exists via a %0a sequence in the url parameter to api/v1/registry.

## References
- https://github.com/netdata/netdata/pull/4521
- https://github.com/netdata/netdata/commit/92327c9ec211bd1616315abcb255861b130b97ca
- https://www.red4sec.com/cve/netdata_log_injection.txt

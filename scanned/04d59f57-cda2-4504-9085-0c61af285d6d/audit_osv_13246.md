# [M] CVE-2018-18839

## Summary
Severity: Medium
Advisory: CVE-2018-18839
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-06-18
Source: https://osv.dev/vulnerability/CVE-2018-18839
Type: osv

## Details
An issue was discovered in Netdata 1.10.0. Full Path Disclosure (FPD) exists via api/v1/alarms. NOTE: the vendor says "is intentional.

## References
- https://github.com/netdata/netdata/pull/4521
- https://www.red4sec.com/cve/netdata_fpd.txt
- https://github.com/netdata/netdata/commit/92327c9ec211bd1616315abcb255861b130b97ca

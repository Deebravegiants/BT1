# [M] CVE-2020-13776

## Summary
Severity: Medium
Advisory: CVE-2020-13776
CVSS: 6.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/CVE-2020-13776
Type: osv

## Details
systemd through v245 mishandles numerical usernames such as ones composed of decimal digits or 0x followed by hex digits, as demonstrated by use of root privileges when privileges of the 0x0 user account were intended. NOTE: this issue exists because of an incomplete fix for CVE-2017-1000082.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IYGLFEKG45EYBJ7TPQMLWROWPTZBEU63/
- https://security.netapp.com/advisory/ntap-20200611-0003/
- https://github.com/systemd/systemd/issues/15985

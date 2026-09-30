# [H] CVE-2017-12467

## Summary
Severity: High
Advisory: CVE-2017-12467
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-07
Source: https://osv.dev/vulnerability/CVE-2017-12467
Type: osv

## Details
Memory leak in CCN-lite before 2.00 allows context-dependent attackers to cause a denial of service (memory consumption) by leveraging failure to allocate memory for the comp or complen structure member.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/133
- https://github.com/cn-uofbasel/ccn-lite/releases/tag/2.0.0

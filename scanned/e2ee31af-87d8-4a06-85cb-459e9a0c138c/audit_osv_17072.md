# [H] CVE-2020-11940

## Summary
Severity: High
Advisory: CVE-2020-11940
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/CVE-2020-11940
Type: osv

## Details
In nDPI through 3.2 Stable, an out-of-bounds read in concat_hash_string in ssh.c can be exploited by a network-positioned attacker that can send malformed SSH protocol messages on a network segment monitored by nDPI's library.

## References
- https://github.com/ntop/nDPI/commit/3bbb0cd3296023f6f922c71d21a1c374d2b0a435
- https://securitylab.github.com/advisories/GHSL-2020-051_052-ntop-ndpi

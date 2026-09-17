# [H] CVE-2018-16855

## Summary
Severity: High
Advisory: CVE-2018-16855
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-16855
Type: osv

## Details
An issue has been found in PowerDNS Recursor before version 4.1.8 where a remote attacker sending a DNS query can trigger an out-of-bounds memory read while computing the hash of the query for a packet cache lookup, possibly leading to a crash.

## References
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2018-09.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16855

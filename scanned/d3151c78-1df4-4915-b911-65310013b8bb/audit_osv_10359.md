# [M] CVE-2017-15105

## Summary
Severity: Medium
Advisory: CVE-2017-15105
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-01-23
Source: https://osv.dev/vulnerability/CVE-2017-15105
Type: osv

## Details
A flaw was found in the way unbound before 1.6.8 validated wildcard-synthesized NSEC records. An improperly validated wildcard NSEC record could be used to prove the non-existence (NXDOMAIN answer) of an existing wildcard record, or trick unbound into accepting a NODATA proof.

## References
- http://www.securityfocus.com/bid/102817
- https://lists.debian.org/debian-lts-announce/2018/01/msg00039.html
- https://lists.debian.org/debian-lts-announce/2019/02/msg00022.html
- https://usn.ubuntu.com/3673-1/
- https://unbound.net/downloads/CVE-2017-15105.txt

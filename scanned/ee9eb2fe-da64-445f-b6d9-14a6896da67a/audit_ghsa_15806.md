# [M] github.com/google/nftable IP addresses were encoded in the wrong byte order

## Summary
Severity: Medium
Advisory: GHSA-qjvf-8748-9w7h
CVE: CVE-2024-6284
CWE: CWE-1286, CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-04
Source: https://github.com/advisories/GHSA-qjvf-8748-9w7h
Type: github-advisory

## Affected
- Go: `github.com/google/nftables` — affected >=0.1.0 <0.2.0

## Details
In  https://github.com/google/nftables IP addresses were encoded in the wrong byte order, resulting in an nftables configuration which does not work as intended (might block or not block the desired addresses).

This issue affects:  https://pkg.go.dev/github.com/google/nftables@v0.1.0 

The bug was fixed in the next released version:  https://pkg.go.dev/github.com/google/nftables@v0.2.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6284
- https://github.com/crowdsecurity/cs-firewall-bouncer/issues/368
- https://github.com/google/nftables/issues/225
- https://github.com/google/nftables/commit/b1f901b05510bed05c232c5049f68d1511b56a19
- https://bugs.launchpad.net/ubuntu/+source/crowdsec-firewall-bouncer/+bug/2069596
- https://github.com/google/nftables

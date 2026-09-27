# [H] Integer Overflow or Wraparound in NATS Server

## Summary
Severity: High
Advisory: GHSA-jp4j-47f9-2vc3
CVE: CVE-2019-13126
CWE: CWE-190
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-jp4j-47f9-2vc3
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.2.0

## Details
An integer overflow in NATS Server before 2.2.0 allows a remote attacker to crash the server by sending a crafted request.

### Specific Go Packages Affected
github.com/nats-io/nats-server/v2/server

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-13126
- https://github.com/nats-io/nats-server/pull/1053
- https://github.com/nats-io/nats-server/pull/1441
- https://github.com/nats-io/nats-server/commit/07ef71ff98f45f8c2711be4aeaf484610d891dda
- https://github.com/nats-io/nats-server/commits/master
- https://www.twistlock.com/labs-blog/finding-dos-vulnerability-nats-go-fuzz-cve-2019-13126

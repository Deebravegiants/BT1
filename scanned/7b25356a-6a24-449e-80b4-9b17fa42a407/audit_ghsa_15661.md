# [H] NATS Server and Streaming Server fails to enforce negative user permissions, may allow denied subjects

## Summary
Severity: High
Advisory: GHSA-2h2x-8hh2-mfq8
CVE: CVE-2022-29946
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-2h2x-8hh2-mfq8
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.8.2
- Go: `github.com/nats-io/nats-streaming-server` — affected >=0 <0.24.6

## Details
NATS.io NATS Server before 2.8.2 and Streaming Server before 0.24.6 could allow a remote attacker to bypass security restrictions, caused by the failure to enforce negative user permissions in one scenario. By using a queue subscription on the wildcard, an attacker could exploit this vulnerability to allow denied subjects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29946
- https://github.com/advisories/GHSA-2h2x-8hh2-mfq8
- https://github.com/nats-io/advisories/blob/main/CVE/CVE-2022-29946.txt

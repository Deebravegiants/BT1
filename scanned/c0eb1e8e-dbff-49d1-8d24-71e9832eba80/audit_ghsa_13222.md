# [C] NATS nats-server allows directory traversal via unintended path to a management action 

## Summary
Severity: Critical
Advisory: GHSA-vpjc-4jcv-jc29
CVE: CVE-2022-28357
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-09-19
Source: https://github.com/advisories/GHSA-vpjc-4jcv-jc29
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server` — affected >=2.2.0 <2.7.4

## Details
NATS nats-server 2.2.0 through 2.7.4 allows directory traversal because of an unintended path to a management action from a management account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-28357
- https://advisories.nats.io/CVE/CVE-2022-28357.txt
- https://github.com/nats-io/nats-server
- https://github.com/nats-io/nats-server/releases/tag/v2.7.4

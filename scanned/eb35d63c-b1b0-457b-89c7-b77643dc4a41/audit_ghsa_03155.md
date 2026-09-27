# [H] Improper Access Control in Lightning Network Daemon

## Summary
Severity: High
Advisory: GHSA-78hj-86cr-6j2v
CVE: CVE-2019-12999
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-78hj-86cr-6j2v
Type: github-advisory

## Affected
- Go: `github.com/lightningnetwork/lnd` — affected >=0 <0.7.1-beta

## Details
Lightning Network Daemon (lnd) before 0.7 allows attackers to trigger loss of funds because of Incorrect Access Control.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12999
- https://github.com/lightninglabs/chanleakcheck
- https://github.com/lightningnetwork/lnd/commits/master
- https://github.com/lightningnetwork/lnd/releases/tag/v0.7.0-beta
- https://lists.linuxfoundation.org/pipermail/lightning-dev/2019-September/002174.html

# [H] xkeys seal encryption used fixed key for all encryption

## Summary
Severity: High
Advisory: GHSA-mr45-rx8q-wcm9
CVE: CVE-2023-46129
CWE: CWE-321, CWE-325
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-mr45-rx8q-wcm9
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nkeys` — affected >=0.4.0 <0.4.6
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.10.0 <2.10.4

## Details
## Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The cryptographic key handling library, nkeys, recently gained support for encryption, not just for signing/authentication.  This is used in nats-server 2.10 (Sep 2023) and newer for authentication callouts.

## Problem Description

The nkeys library's "xkeys" encryption handling logic mistakenly passed an array by value into an internal function, where the function mutated that buffer to populate the encryption key to use.  As a result, all encryption was actually to an all-zeros key.

This affects encryption only, not signing.  
FIXME: FILL IN IMPACT ON NATS-SERVER AUTH CALLOUT SECURITY.

## Affected versions

nkeys Go library:
 * 0.4.0 up to and including 0.4.5
 * Fixed with nats-io/nkeys: 0.4.6

NATS Server:
 * 2.10.0 up to and including 2.10.3
 * Fixed with nats-io/nats-server: 2.10.4

## Solution

Upgrade the nats-server.  
For any application handling auth callouts in Go, if using the nkeys library, update the dependency, recompile and deploy that in lockstep.

## Credits

Problem reported by Quentin Matillat (GitHub @tinou98).

## References
- https://github.com/nats-io/nkeys/security/advisories/GHSA-mr45-rx8q-wcm9
- https://nvd.nist.gov/vuln/detail/CVE-2023-46129
- https://github.com/nats-io/nkeys/commit/58fb9d69f42ea73fffad1d14e5914dc666f3daa1
- https://github.com/nats-io/nkeys
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/R3UETKPUB3V5JS5TLZOF3SMTGT5K5APS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ULQQONMSCQSH5Z5OWFFQHCGEZ3NL4DRJ
- http://www.openwall.com/lists/oss-security/2023/10/31/1

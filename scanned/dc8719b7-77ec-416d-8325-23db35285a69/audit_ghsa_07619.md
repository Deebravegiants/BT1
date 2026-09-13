# [M] Pion DTLS's usage of random nonce generation with AES GCM ciphers risks leaking the authentication key

## Summary
Severity: Medium
Advisory: GHSA-9f3f-wv7r-qc8r
CVE: CVE-2026-26014
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-11
Source: https://github.com/advisories/GHSA-9f3f-wv7r-qc8r
Type: github-advisory

## Affected
- Go: `github.com/pion/dtls/v3` — affected >=3.1.0 <3.1.1
- Go: `github.com/pion/dtls/v2` — affected >=0
- Go: `github.com/pion/dtls` — affected >=0
- Go: `github.com/pion/dtls/v3` — affected >=0 <3.0.11

## Details
### Impact
Pion DTLS versions v1.0.0 through v3.0.10 use random nonce generation with AES GCM ciphers, which makes it easier for remote attackers to obtain the authentication key and spoof data by leveraging the reuse of a nonce in a session and a "forbidden attack". 

### Patches
Upgrade to v3.1.1 or later. This version includes PR #796, which uses the 64-bit sequence number to populate the `nonce_explicit` part of the GCM nonce. This is according to best practice outlined in [RFC 9325 section 7.2.1](https://www.rfc-editor.org/rfc/rfc9325#section-7.2.1). 

v3.0.11 is a backport patch supporting Go v1.21

### Workarounds
There are no workarounds without upgrading to version v3.0.11, v3.1.1 or later.

### References
Commit fixing the bug: https://github.com/pion/dtls/commit/61762dee8217991882c5eb79856b9e7a73ee349f
Commit fixing the bug (backport): 90e241c
Pull request: #796

## References
- https://github.com/pion/dtls/security/advisories/GHSA-9f3f-wv7r-qc8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-26014
- https://github.com/pion/dtls/pull/796
- https://github.com/pion/dtls/commit/61762dee8217991882c5eb79856b9e7a73ee349f
- https://github.com/pion/dtls/commit/90e241cfec2985715efdd3d005972847462a67d6
- https://github.com/pion/dtls
- https://github.com/pion/dtls/releases/tag/v3.0.11
- https://github.com/pion/dtls/releases/tag/v3.1.1

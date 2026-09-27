# [M] uTLS ServerHellos are accepted without checking TLS 1.3 downgrade canaries

## Summary
Severity: Medium
Advisory: GHSA-pmc3-p9hx-jq96
CVE: CVE-2026-26994
CWE: CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-23
Source: https://github.com/advisories/GHSA-pmc3-p9hx-jq96
Type: github-advisory

## Affected
- Go: `github.com/refraction-networking/utls` — affected >=0 <1.7.0

## Details
### Description
Before version 1.7.0, utls did not implement the TLS 1.3 downgrade protection mechanism specified in RFC 8446 Section 4.1.3 when using a utls ClientHello spec. This allowed an active network adversary to downgrade TLS 1.3 connections initiated by a utls client to a lower TLS version (e.g., TLS 1.2) by modifying the ClientHello message to exclude the SupportedVersions extension, causing the server to respond with a TLS 1.2 ServerHello (along with a downgrade canary in the ServerHello random field). Because utls did not check the downgrade canary in the ServerHello random field, clients would accept the downgraded connection without detecting the attack. This attack could also be used by an active network attacker to fingerprint utls connections.

### Fix Commit or Pull Request

refraction-networking/utls#337, specifically refraction-networking/utls@f8892761e2a4d29054264651d3a86fda83bc83f9

### References

- https://github.com/refraction-networking/utls/issues/181

## References
- https://github.com/refraction-networking/utls/security/advisories/GHSA-pmc3-p9hx-jq96
- https://nvd.nist.gov/vuln/detail/CVE-2026-26994
- https://github.com/refraction-networking/utls/issues/181
- https://github.com/refraction-networking/utls/pull/337
- https://github.com/refraction-networking/utls/commit/f8892761e2a4d29054264651d3a86fda83bc83f9
- https://github.com/refraction-networking/utls

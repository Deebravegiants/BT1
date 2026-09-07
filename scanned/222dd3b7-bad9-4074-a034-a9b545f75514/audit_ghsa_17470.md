# [M] Envoy's TLS certificate matcher for `match_typed_subject_alt_names` may incorrectly treat certificates containing an embedded null byte

## Summary
Severity: Medium
Advisory: GHSA-rwjg-c3h2-f57p
CVE: CVE-2025-66220
CWE: CWE-170
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-12-05
Source: https://github.com/advisories/GHSA-rwjg-c3h2-f57p
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0 <1.36.3
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0 <1.35.7
- Go: `github.com/envoyproxy/envoy` — affected >=1.34.0 <1.34.11
- Go: `github.com/envoyproxy/envoy` — affected >=0 <1.33.13

## Details
### Summary
Envoy’s mTLS certificate matcher for `match_typed_subject_alt_names` may incorrectly treat certificates containing an embedded null byte (\0) inside an `OTHERNAME` SAN value as valid matches.

### Details
This occurs when the SAN is encoded as a `BMPSTRING` or `UNIVERSALSTRING`, and its UTF-8 conversion result is truncated at the first null byte during string assignment. As a result, `"victim\0evil"` may match an exact: `"victim"` rule and be accepted by Envoy.

### PoC

Create a CA and a server certificate signed by that CA.
Create two client certificates signed by the same CA:
client_evil with OTHERNAME BMPSTRING = "evil"
client_null with OTHERNAME BMPSTRING = "victim\0evil"
Configure Envoy with require_client_certificate: true and a match_typed_subject_alt_names entry for the OTHERNAME OID with matcher.exact: "victim".
Connect without a client cert → connection rejected.
Connect with client_evil → connection rejected.
Connect with client_null → connection accepted (but shouldn't!).

### Impact
An attacker who can obtain a trusted client certificate with a null byte embedded in an OTHERNAME SAN can exploit this vulnerability. The practical impact is unauthorized impersonation of the matched identity, enabling access to services or APIs protected by that exact OTHERNAME check.

### Credit
[markevich.nikita1@gmail.com](mailto:markevich.nikita1@gmail.com)

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-rwjg-c3h2-f57p
- https://nvd.nist.gov/vuln/detail/CVE-2025-66220
- https://github.com/envoyproxy/envoy

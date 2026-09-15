# [C] Mellium allows Authentication Bypass by Spoofing

## Summary
Severity: Critical
Advisory: GHSA-98hf-m87w-cq6h
CVE: CVE-2024-46957
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-25
Source: https://github.com/advisories/GHSA-98hf-m87w-cq6h
Type: github-advisory

## Affected
- Go: `mellium.im/xmpp` — affected >=0 <0.22.0

## Details
Mellium mellium.im/xmpp 0.0.1 through 0.21.4 allows response spoofing because the stanza type is not checked. This is fixed in 0.22.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-46957
- https://codeberg.org/mellium/xmpp
- https://codeberg.org/mellium/xmpp/releases
- https://codeberg.org/mellium/xmpp/releases/tag/v0.22.0
- https://mellium.im/cve/cve-2024-46957

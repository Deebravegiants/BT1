# [H] Clatter has a PSK Validity Rule Violation issue

## Summary
Severity: High
Advisory: GHSA-253q-9q78-63x4
CVE: CVE-2026-24785
CWE: CWE-327
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-01-28
Source: https://github.com/advisories/GHSA-253q-9q78-63x4
Type: github-advisory

## Affected
- crates.io: `clatter` — affected >=0 <2.2.0

## Details
### Impact

Protocol compliance vulnerability. The library allowed post-quantum handshake patterns that violated the PSK validity rule (Noise Protocol Framework Section 9.3). This could allow PSK-derived keys to be used for encryption without proper randomization by self-chosen ephemeral randomness, weakening security guarantees and potentially allowing catastrophic key reuse.

Affected default patterns include `noise_pqkk_psk0`, `noise_pqkn_psk0`, `noise_pqnk_psk0`, `noise_pqnn_psk0`, and some hybrid variants. Users of these patterns may have been using handshakes that do not meet the intended security properties.

### Patches

The issue is fully patched and released in Clatter v2.2.0. The fixed version includes runtime checks to detect offending handshake patterns.

### Workarounds

Avoid using offending `*_psk0` variants of post-quantum patterns. Review custom handshake patterns carefully.

### Resources

* [PSK validity rule](https://noiseprotocol.org/noise.html#validity-rule)

## References
- https://github.com/jmlepisto/clatter/security/advisories/GHSA-253q-9q78-63x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-24785
- https://github.com/jmlepisto/clatter/commit/b65ae6e9b8019bed5407771e21f89ddff17c5a71
- https://github.com/jmlepisto/clatter
- https://noiseprotocol.org/noise.html#validity-rule

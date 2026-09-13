# [H] Undici: Malicious WebSocket 64-bit length overflows parser and crashes the client

## Summary
Severity: High
Advisory: GHSA-f269-vfmq-vjvj
CVE: CVE-2026-1528
CWE: CWE-1284, CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-13
Source: https://github.com/advisories/GHSA-f269-vfmq-vjvj
Type: github-advisory

## Affected
- npm: `undici` — affected >=6.0.0 <6.24.0
- npm: `undici` — affected >=7.0.0 <7.24.0

## Details
### Impact
A server can reply with a WebSocket frame using the 64-bit length form and an extremely large length. undici's ByteParser overflows internal math, ends up in an invalid state, and throws a fatal TypeError that terminates the process. 

### Patches


 Patched in the undici version v7.24.0 and v6.24.0. Users should upgrade to this version or later.

### Workarounds

There are no workarounds.

## References
- https://github.com/nodejs/undici/security/advisories/GHSA-f269-vfmq-vjvj
- https://nvd.nist.gov/vuln/detail/CVE-2026-1528
- https://hackerone.com/reports/3537648
- https://cna.openjsf.org/security-advisories.html
- https://github.com/nodejs/undici

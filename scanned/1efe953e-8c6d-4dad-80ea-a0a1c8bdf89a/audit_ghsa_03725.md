# [H] rendertron LFI vulnerability

## Summary
Severity: High
Advisory: GHSA-j87c-cj65-vmh5
CVE: CVE-2017-18354
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-j87c-cj65-vmh5
Type: github-advisory

## Affected
- npm: `rendertron` — affected >=0 <1.1.0

## Details
Rendertron 1.0.0 allows for alternative protocols such as 'file://' introducing a Local File Inclusion (LFI) bug where arbitrary files can be read by a remote attacker.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18354
- https://github.com/GoogleChrome/rendertron/pull/88
- https://github.com/GoogleChrome/rendertron/commit/8d70628c96ae72eff6eebb451d26fc9ed6b58b0e
- https://bugs.chromium.org/p/chromium/issues/detail?id=759111
- https://github.com/GoogleChrome/rendertron
- https://github.com/advisories/GHSA-j87c-cj65-vmh5

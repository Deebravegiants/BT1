# [H] Improper Key Verification in ipns

## Summary
Severity: High
Advisory: GHSA-j59f-6m4q-62h6
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-05-30
Source: https://github.com/advisories/GHSA-j59f-6m4q-62h6
Type: github-advisory

## Affected
- npm: `ipns` — affected >=0 <0.1.3

## Details
Versions 0.1.1 or 0.1.2 of `ipns` are vulnerable to improper key validation. This is due to the public key verification was not being performed properly, resulting in any key being valid.


## Recommendation

Update to version 0.1.3 or later.

## References
- https://github.com/ipfs/js-ipns/commit/33684e356f1f2fdcd99b2fb85fcc5d52223769a0
- https://www.npmjs.com/advisories/693

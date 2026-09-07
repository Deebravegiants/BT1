# [M] OpenClaw: Matrix Verification Notices Bypass Matrix DM Policy and Reply to Unpaired DM Peers

## Summary
Severity: Medium
Advisory: GHSA-9wqx-g2cw-vc7r
CVE: CVE-2026-35647
CWE: CWE-288, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-9wqx-g2cw-vc7r
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0

## Details
## Summary

Matrix Verification Notices Bypass Matrix DM Policy and Reply to Unpaired DM Peers

## Affected Packages / Versions

- Package: `openclaw`
- Affected versions: `<= 2026.3.24`
- First patched version: `2026.3.25`
- Latest published npm version at verification time: `2026.3.24`

## Details

Matrix verification notices previously bypassed DM access checks and could reply to peers that were unpaired or otherwise outside the allowed DM policy. Commit `2383daf5c4a4e08d9553e0e949552ad755ef9ec2` gates verification notices on DM access before sending.

Verified vulnerable on tag `v2026.3.24` and fixed on `main` by commit `2383daf5c4a4e08d9553e0e949552ad755ef9ec2`.

## Fix Commit(s)

- `2383daf5c4a4e08d9553e0e949552ad755ef9ec2`

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-9wqx-g2cw-vc7r
- https://github.com/openclaw/openclaw/commit/2383daf5c4a4e08d9553e0e949552ad755ef9ec2
- https://github.com/openclaw/openclaw

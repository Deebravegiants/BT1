# [M] OpenClaw: Unauthorized Telegram Senders Trigger Media Download and Disk Write Before Access Check

## Summary
Severity: Medium
Advisory: GHSA-h656-5vcf-cm23
CWE: CWE-208, CWE-404, CWE-406, CWE-770
Ecosystem: npm
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-h656-5vcf-cm23
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
## Impact

In Telegram DM mode, inbound media was downloaded and written to disk before sender authorization checks completed. An unauthorized sender could trigger inbound media download/write activity (including media groups) even when DM access should be denied.

## Affected Packages / Versions

- Package: `openclaw` (npm)
- Latest published version currently affected: `2026.2.23`
- Vulnerable range: `<= 2026.2.23`
- Patched in planned next release: `2026.2.24`

## Fix Commit(s)

- `9514201fb9b51de5d0b23151110d0ff5d9c8bd67`

## Technical Details

The Telegram handler flow now enforces DM authorization before media download/write paths execute, including media-group handling. Inbound channel activity tracking was also moved to run after DM authorization in the Telegram message context path.

## Release Process Note

`patched_versions` is pre-set to the planned next release (`2026.2.24`). After npm publish, the advisory can be published without further version-field edits.

OpenClaw thanks @v8hid for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-h656-5vcf-cm23
- https://github.com/openclaw/openclaw/commit/9514201fb9b51de5d0b23151110d0ff5d9c8bd67
- https://github.com/openclaw/openclaw

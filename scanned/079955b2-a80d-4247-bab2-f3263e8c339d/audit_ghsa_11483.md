# [H] OpenClaw: Message action attachment hydration bypasses local media root checks when sandboxRoot is unset

## Summary
Severity: High
Advisory: GHSA-fqcm-97m6-w7rm
CVE: CVE-2026-27522
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-fqcm-97m6-w7rm
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.24

## Details
## Impact
`sendAttachment` and `setGroupIcon` message actions could hydrate media from local absolute paths when `sandboxRoot` was unset, bypassing intended local media root checks. This could allow reads of arbitrary host files reachable by the runtime user when an authorized message-action path was triggered.

## Affected Packages / Versions
- Package: `openclaw` (npm)
- Latest published npm version at triage: `2026.2.23`
- Vulnerable: `<= 2026.2.23`
- Patched in code: `>= 2026.2.24` (planned next release)

## Remediation
Upgrade to `openclaw` `2026.2.24` or later once published.

## Fix Commit(s)
- 270ab03e379f9653e15f7033c9830399b66b7e51

## Release Process Note
`patched_versions` is pre-set to the planned next release (`>= 2026.2.24`). Once that npm release is published, this advisory can be published without further field edits.

OpenClaw thanks @GCXWLP for reporting.


### Publication Update (2026-02-25)
`openclaw@2026.2.24` is published on npm and contains the fix commit(s) listed above. This advisory now marks `>= 2026.2.24` as patched.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-fqcm-97m6-w7rm
- https://nvd.nist.gov/vuln/detail/CVE-2026-27522
- https://github.com/openclaw/openclaw/commit/270ab03e379f9653e15f7033c9830399b66b7e51
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-arbitrary-file-read-via-sendattachment-and-setgroupicon-message-actions

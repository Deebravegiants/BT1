# [H] OpenClaw vulnerable to sensitive file disclosure via stageSandboxMedia

## Summary
Severity: High
Advisory: GHSA-x9cf-3w63-rpq9
CVE: CVE-2026-32030
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-x9cf-3w63-rpq9
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.19

## Details
### Summary
When iMessage remote attachment fetching is enabled (`channels.imessage.remoteHost`), `stageSandboxMedia` accepted arbitrary absolute paths and used SCP to copy them into local staging.

If a non-attachment path reaches this flow, files outside expected iMessage attachment directories on the remote host can be staged.

### Affected Packages / Versions
- Package: `openclaw`
- Affected: up to and including `2026.2.17` (latest npm version as of February 19, 2026)
- Fixed: pending next release with remote attachment path validation

### Impact
Confidentiality impact. An attacker who can influence inbound attachment path metadata may disclose files readable by the OpenClaw process on the configured remote host.

### Attack Preconditions
1. iMessage attachments enabled (`channels.imessage.includeAttachments=true`), and
2. remote attachment mode active (`channels.imessage.remoteHost` configured or auto-detected), and
3. attacker can inject/tamper with attachment path metadata.

Given these preconditions, this advisory is assessed as **medium** severity.


## Fix Commit(s)
- `1316e5740382926e45a42097b4bfe0aef7d63e8e`

### Release Process Note
`patched_versions` should be set to the next released npm version that includes remote attachment path validation, then the advisory can be published.

### Mitigation
- Upgrade to the first release that includes remote attachment path validation.
- If remote attachments are not required, disable iMessage attachment ingestion.
- Run OpenClaw under least privilege on the remote host.

OpenClaw thanks @zpbrent for reporting.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-x9cf-3w63-rpq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-32030
- https://github.com/openclaw/openclaw/commit/1316e5740382926e45a42097b4bfe0aef7d63e8e
- https://github.com/openclaw/openclaw
- https://www.vulncheck.com/advisories/openclaw-sensitive-file-disclosure-via-stagesandboxmedia-path-traversal

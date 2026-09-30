# [H] OpenClaw has a LFI in BlueBubbles media path handling

## Summary
Severity: High
Advisory: GHSA-rwj8-p9vq-25gv
CVE: CVE-2026-29611
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-rwj8-p9vq-25gv
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.2.14

## Details
### Summary
The BlueBubbles extension accepted attacker-controlled local filesystem paths via `mediaPath` and could read arbitrary local files from disk before sending them as media attachments.

### Details
When `sendBlueBubblesMedia` received a non-HTTP media source, the previous implementation resolved it to a local path and read it directly from disk. There was no required allowlist of safe directories, so values like `/etc/passwd` (or equivalent sensitive paths on other platforms) could be requested and exfiltrated.

The fix hardens local media loading by requiring explicit configured roots (`channels.bluebubbles.mediaLocalRoots`) and by enforcing canonical-path containment checks before reading local files. Paths outside allowed roots are rejected.

Fix PR: https://github.com/openclaw/openclaw/pull/16322
Fix commit: https://github.com/openclaw/openclaw/commit/71f357d9498cebb0efe016b0496d5fbe807539fc

### Affected Packages / Versions
- Package: `openclaw` (npm)
- Affected: `< v2026.2.14`
- Fixed: `>= v2026.2.14` (planned)

### Impact
An attacker able to trigger BlueBubbles media sends could exfiltrate local files accessible to the OpenClaw process.

### Remediation
Upgrade to a release that includes commit `71f357d9498cebb0efe016b0496d5fbe807539fc` and configure `channels.bluebubbles.mediaLocalRoots` to explicit trusted directories.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-rwj8-p9vq-25gv
- https://github.com/openclaw/openclaw/pull/16322
- https://github.com/openclaw/openclaw/commit/71f357d9498cebb0efe016b0496d5fbe807539fc
- https://github.com/openclaw/openclaw
- https://github.com/openclaw/openclaw/releases/tag/v2026.2.14

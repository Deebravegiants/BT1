# [M] OpenClaw Vulnerable to Local File Inclusion via MEDIA: Path Extraction

## Summary
Severity: Medium
Advisory: GHSA-r8g4-86fx-92mq
CVE: CVE-2026-25475
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-r8g4-86fx-92mq
Type: github-advisory

## Affected
- npm: `openclaw` — affected >=0 <2026.1.30

## Details
### Summary
The `isValidMedia()` function in `src/media/parse.ts` allows arbitrary file paths including absolute paths, home directory paths, and directory traversal sequences. An agent can read any file on the system by outputting `MEDIA:/path/to/file`, exfiltrating sensitive data to the user/channel.

### Details
**Location:** `src/media/parse.ts:17-27`

The path validation accepts dangerous patterns:

```typescript
function isValidMedia(candidate: string, opts?: { allowSpaces?: boolean }) {
  if (candidate.startsWith("/")) return true;      // ALLOWS /etc/passwd
  if (candidate.startsWith("./")) return true;
  if (candidate.startsWith("../")) return true;    // ALLOWS ../../etc/passwd
  if (candidate.startsWith("~")) return true;      // ALLOWS ~/secrets
  return false;
}
```

No validation ensures the path is within a safe directory or is actually a media file.

### PoC

Agent outputs any of:
```
MEDIA:/etc/passwd
MEDIA:~/.ssh/id_rsa
MEDIA:~/.aws/credentials
MEDIA:../../../etc/passwd
```

The file contents are rendered/sent to the requesting user or channel.

### Impact
- Read ANY file accessible to the agent user
- Exfiltrate SSH keys (`~/.ssh/id_rsa`)
- Steal cloud credentials (`~/.aws/credentials`)
- Access API keys (`.env`, `config.json`)
- Read system files (`/etc/passwd`, `/etc/shadow`)

**Note:** PR #4930 contains a fix but is NOT MERGED - production is vulnerable.

## References
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r8g4-86fx-92mq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25475
- https://github.com/openclaw/openclaw

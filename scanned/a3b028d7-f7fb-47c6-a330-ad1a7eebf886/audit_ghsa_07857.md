# [C] Basic FTP has Path Traversal Vulnerability in its downloadToDir() method

## Summary
Severity: Critical
Advisory: GHSA-5rq4-664w-9x2c
CVE: CVE-2026-27699
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-5rq4-664w-9x2c
Type: github-advisory

## Affected
- npm: `basic-ftp` — affected >=0 <5.2.0

## Details
The `basic-ftp` library contains a path traversal vulnerability in the `downloadToDir()` method. A malicious FTP server can send directory listings with filenames containing path traversal sequences (`../`) that cause files to be written outside the intended download directory.


## Source-to-Sink Flow

```
1. SOURCE: FTP server sends LIST response
└─> "-rw-r--r-- 1 user group 1024 Jan 20 12:00 ../../../etc/passwd"

2. PARSER: parseListUnix.ts:100 extracts filename
└─> file.name = "../../../etc/passwd"

3. VALIDATION: parseListUnix.ts:101 checks
└─> if (name === "." || name === "..") ❌ (only filters exact matches)
└─> "../../../etc/passwd" !== "." && !== ".." ✅ PASSES

4. SINK: Client.ts:707 uses filename directly
└─> const localPath = join(localDirPath, file.name)
└─> join("/safe/download", "../../../etc/passwd")
└─> Result: "/safe/download/../../../etc/passwd" → resolves to "/etc/passwd"

5. FILE WRITE: Client.ts:512 opens file
└─> fsOpen(localPath, "w") → writes to /etc/passwd (outside intended directory)
```

## Vulnerable Code

**File**: `src/Client.ts:707`

```typescript
protected async _downloadFromWorkingDir(localDirPath: string): Promise<void> {
await ensureLocalDirectory(localDirPath)
for (const file of await this.list()) {
const localPath = join(localDirPath, file.name) // ⚠️ VULNERABLE
// file.name comes from untrusted FTP server, no sanitization
await this.downloadTo(localPath, file.name)
}
}
```

**Root Cause**:
- Parser validation (`parseListUnix.ts:101`) only filters exact `.` or `..` entries
- No sanitization of `../` sequences in filenames
- `path.join()` doesn't prevent traversal, `fs.open()` resolves paths


# Impact

A malicious FTP server can:
- Write files to arbitrary locations on the client filesystem
- Overwrite critical system files (if user has write access)
- Potentially achieve remote code execution

## Affected Versions

- **Tested**: v5.1.0
- **Likely**: All versions (code pattern exists since initial implementation)

## Mitigation

**Workaround**: Do not use `downloadToDir()` with untrusted FTP servers.

**Fix**: Sanitize filenames before use:

```typescript
import { basename } from 'path'

// In _downloadFromWorkingDir:
const sanitizedName = basename(file.name) // Strip path components
const localPath = join(localDirPath, sanitizedName)
```

## References
- https://github.com/patrickjuchli/basic-ftp/security/advisories/GHSA-5rq4-664w-9x2c
- https://nvd.nist.gov/vuln/detail/CVE-2026-27699
- https://github.com/patrickjuchli/basic-ftp/commit/2a2a0e6514357b9eda07c2f8afbd3f04727a7cd9
- https://github.com/patrickjuchli/basic-ftp
- https://github.com/patrickjuchli/basic-ftp/releases/tag/v5.2.0

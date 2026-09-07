# [M] FileBrowser Vulnerable to Stored XSS via SVG File in Public Share (Missing CSP Header)

## Summary
Severity: Medium
Advisory: GHSA-mmpx-jh39-wrv6
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-mmpx-jh39-wrv6
Type: github-advisory

## Affected
- Go: `github.com/gtsteffaniak/filebrowser` — affected >=0 <0.0.0-20260501184955-6bfc3974192e

## Details
## Summary

FileBrowser Quantum serves inline SVG files without a `Content-Security-Policy` header, allowing embedded JavaScript in SVG files to execute when accessed via public share links.

Verified on v1.3.0-stable.

## Affected product

- **Product:** FileBrowser Quantum (`gtsteffaniak/filebrowser`)
- **Verified version:** v1.3.0-stable
- **Docker image:** gtstef/filebrowser:latest
- **Affected endpoint:** `GET /public/api/resources/download?hash=HASH&inline=true`
- **CWE:** CWE-79 — Cross-site Scripting (Stored)

## Impact

- **Stored XSS** — Malicious SVG persists and executes for every visitor to the share link
- **No authentication required to trigger** — Public share links are accessible to anyone
- **Session hijacking** — If authenticated users click the link, their session can be stolen
- **Phishing** — Attacker can redirect or overlay fake login forms

## Reproduction

1. Login as any user with upload permission
2. Upload SVG file:
   ```xml
   <svg xmlns="http://www.w3.org/2000/svg">
     <script>alert(document.domain)</script>
   </svg>
   ```
3. Create public share for the file
4. Access the share link with `?inline=true`
5. JavaScript executes in browser

## Root cause

The inline download endpoint returns SVG files with:
```
Content-Type: image/svg+xml
Content-Disposition: inline; filename="xss.svg"
X-Content-Type-Options: nosniff
```

But no CSP header to block script execution. The upstream project (filebrowser/filebrowser) mitigates this with:
```
Content-Security-Policy: script-src 'none'
```

## Suggested fix

Add CSP header on inline file downloads:

```go
w.Header().Set("Content-Security-Policy", "script-src 'none'")
```

This matches the upstream filebrowser/filebrowser implementation.

## References
- https://github.com/gtsteffaniak/filebrowser/security/advisories/GHSA-mmpx-jh39-wrv6
- https://github.com/gtsteffaniak/filebrowser/commit/6bfc3974192e954f71cc5d1cd04baaaec3b76383
- https://github.com/gtsteffaniak/filebrowser

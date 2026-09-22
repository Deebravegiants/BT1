# [H] Listing of upload directory contents possible

## Summary
Severity: High
Advisory: GHSA-qmfx-75ff-8mw6
Ecosystem: Go
Published: 2021-05-27
Source: https://github.com/advisories/GHSA-qmfx-75ff-8mw6
Type: github-advisory

## Affected
- Go: `github.com/ThomasLeister/prosody-filer` — affected >=0 <1.0.1

## Details
There's an security issue in prosody-filer versions **< 1.0.1** which leads to unwanted directory listings of download directories. 

An attacker is able to list previous uploads of a certain user by shortening the URL and accessing a URL subdirectors other than `/upload/` (or the corresponding user defined root dir)

Version 1.0.1 and later fix this problem and allow only direct file access if the full path is known. Directory listings are blocked entirely.

## References
- https://github.com/ThomasLeister/prosody-filer/security/advisories/GHSA-qmfx-75ff-8mw6

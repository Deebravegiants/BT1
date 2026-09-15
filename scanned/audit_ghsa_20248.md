# [C] Path Traversal in file editor on Windows in Gogs

## Summary
Severity: Critical
Advisory: GHSA-994f-7g86-qr56
CVE: CVE-2022-1992
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-06-08
Source: https://github.com/advisories/GHSA-994f-7g86-qr56
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.9

## Details
### Impact

The malicious user is able to delete and upload arbitrary file(s). All installations on Windows with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) are affected.

### Patches

Path cleaning has accommodated for Windows. Users should upgrade to 0.12.9 or the latest 0.13.0+dev.

### Workarounds

N/A

### References

https://huntr.dev/bounties/2e8cdc57-a9cf-46ae-9088-87f09e6c90ab/

### For more information

If you have any questions or comments about this advisory, please post on #7001.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-994f-7g86-qr56
- https://nvd.nist.gov/vuln/detail/CVE-2022-1992
- https://github.com/gogs/gogs/commit/2ca014250fbf0bba94c914d9e43b1f6d8eca3bb0
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129
- https://huntr.dev/bounties/2e8cdc57-a9cf-46ae-9088-87f09e6c90ab

# [C] Gogs OS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-pfvh-p8qp-9ww9
CVE: CVE-2022-2024
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-pfvh-p8qp-9ww9
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.11

## Details
### Impact

The malicious user is able to update a crafted `config` file into repository's `.git` directory in combination with crafted file deletion to gain SSH access to the server on case-insensitive file systems. All installations with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) on case-insensitive file systems (Windows, macOS, etc.) are affected.

### Patches

Make sanitization of upload path to `.git` directory to be case-insensitive. Users should upgrade to 0.12.11 or the latest 0.13.0+dev.

### Workarounds

Disable [repository upload](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129).

### References

https://huntr.dev/bounties/18cf9256-23ab-4098-a769-85f8da130f97/

### For more information

If you have any questions or comments about this advisory, please post on https://github.com/gogs/gogs/issues/7030.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-pfvh-p8qp-9ww9
- https://nvd.nist.gov/vuln/detail/CVE-2022-2024
- https://github.com/gogs/gogs/issues/7030
- https://github.com/gogs/gogs/commit/15d0d6a94be0098a8227b6b95bdf2daed105ec41
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129
- https://huntr.dev/bounties/18cf9256-23ab-4098-a769-85f8da130f97

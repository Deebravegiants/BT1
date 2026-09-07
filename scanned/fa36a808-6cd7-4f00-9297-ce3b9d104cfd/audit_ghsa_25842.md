# [H] Unrestricted Upload of File with Dangerous Type in Gogs

## Summary
Severity: High
Advisory: GHSA-5gjh-5j4f-cpwv
CVE: CVE-2022-0415
CWE: CWE-20, CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-28
Source: https://github.com/advisories/GHSA-5gjh-5j4f-cpwv
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.6

## Details
### Impact

The malicious user is able to upload a crafted `config` file into repository's `.git` directory with to gain SSH access to the server. All installations with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) are affected.

### Patches

Repository file uploads are prohibited to its `.git` directory. Users should upgrade to 0.12.6 or the latest 0.13.0+dev.

### Workarounds

[Disable repository files upload](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L128-L129).

### References

https://huntr.dev/bounties/b4928cfe-4110-462f-a180-6d5673797902/

### For more information

If you have any questions or comments about this advisory, please post on #6833.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-5gjh-5j4f-cpwv
- https://nvd.nist.gov/vuln/detail/CVE-2022-0415
- https://github.com/gogs/gogs/issues/6833
- https://github.com/gogs/gogs/pull/6838
- https://github.com/gogs/gogs/commit/0fef3c9082269e9a4e817274942a5d7c50617284
- https://github.com/gogs/gogs
- https://huntr.dev/bounties/b4928cfe-4110-462f-a180-6d5673797902

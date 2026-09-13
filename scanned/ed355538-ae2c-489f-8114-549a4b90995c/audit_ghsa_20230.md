# [C] OS Command Injection in gogs

## Summary
Severity: Critical
Advisory: GHSA-958j-443g-7mm7
CVE: CVE-2022-1884
CWE: CWE-77, CWE-78
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-02
Source: https://github.com/advisories/GHSA-958j-443g-7mm7
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.8

## Details
### Impact

The malicious user is able to upload a crafted `config` file into repository's `.git` directory with to gain SSH access to the server. All Windows installations with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) are affected.

### Patches

Repository file uploads are prohibited to its `.git` directory. Users should upgrade to 0.12.8 or the latest 0.13.0+dev.

### Workarounds

[Disable repository files upload](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L128-L129).

### References

https://www.huntr.dev/bounties/9cd4e7b7-0979-4e5e-9a1c-388b58dea76b/

### For more information

If you have any questions or comments about this advisory, please post on #6968.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-958j-443g-7mm7
- https://nvd.nist.gov/vuln/detail/CVE-2022-1884
- https://github.com/gogs/gogs/issues/6968
- https://github.com/gogs/gogs/pull/6970
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129
- https://github.com/gogs/gogs/releases/tag/v0.12.8
- https://huntr.com/bounties/9cd4e7b7-0979-4e5e-9a1c-388b58dea76b
- https://www.huntr.dev/bounties/9cd4e7b7-0979-4e5e-9a1c-388b58dea76b

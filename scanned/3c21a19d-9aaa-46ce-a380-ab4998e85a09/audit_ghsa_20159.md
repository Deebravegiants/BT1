# [C] OS Command Injection in file editor in Gogs

## Summary
Severity: Critical
Advisory: GHSA-67mx-jc2f-jgjm
CVE: CVE-2022-1986
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-08
Source: https://github.com/advisories/GHSA-67mx-jc2f-jgjm
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.9

## Details
### Impact

The malicious user is able to update a crafted `config` file into repository's `.git` directory in combination with crafted file deletion to gain SSH access to the server. All installations with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) are affected.

### Patches

File deletions are prohibited to repository's `.git` directory. Users should upgrade to 0.12.9 or the latest 0.13.0+dev.

### Workarounds

N/A

### References

https://huntr.dev/bounties/776e8f29-ff5e-4501-bb9f-0bd335007930/

### For more information

If you have any questions or comments about this advisory, please post on #7000.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-67mx-jc2f-jgjm
- https://nvd.nist.gov/vuln/detail/CVE-2022-1986
- https://github.com/gogs/gogs/commit/38aff73251cc46ced96dd608dab6190415032a82
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129
- https://huntr.dev/bounties/776e8f29-ff5e-4501-bb9f-0bd335007930

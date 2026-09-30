# [C] OS Command Injection in gogs

## Summary
Severity: Critical
Advisory: GHSA-56j7-2pm8-rgmx
CVE: CVE-2021-32546
CWE: CWE-78
Ecosystem: Go
Published: 2022-06-02
Source: https://github.com/advisories/GHSA-56j7-2pm8-rgmx
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.8

## Details
### Impact

The malicious user is able to update a crafted `config` file into repository's `.git` directory with to gain SSH access to the server. All installations with [repository upload enabled (default)](https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129) are affected.

### Patches

Repository file updates are prohibited to its `.git` directory. Users should upgrade to 0.12.8 or the latest 0.13.0+dev.

### Workarounds

N/A

### References

N/A

### For more information

If you have any questions or comments about this advisory, please post on #6555.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-56j7-2pm8-rgmx
- https://nvd.nist.gov/vuln/detail/CVE-2021-32546
- https://github.com/gogs/gogs/issues/6555
- https://github.com/gogs/gogs/pull/6986
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/blob/f36eeedbf89328ee70cc3a2e239f6314f9021f58/conf/app.ini#L127-L129
- https://github.com/gogs/gogs/releases
- https://github.com/gogs/gogs/releases/tag/v0.12.8

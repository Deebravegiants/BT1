# [C] Maliciously crafted Git server replies can lead to path traversal and RCE on go-git clients

## Summary
Severity: Critical
Advisory: GHSA-449p-3h89-pw88
CVE: CVE-2023-49569
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-10
Source: https://github.com/advisories/GHSA-449p-3h89-pw88
Type: github-advisory

## Affected
- Go: `github.com/go-git/go-git/v5` — affected >=5.0.0 <5.11.0
- Go: `gopkg.in/src-d/go-git.v4` — affected >=4.0.0

## Details
### Impact
A path traversal vulnerability was discovered in go-git versions prior to `v5.11`. This vulnerability allows an attacker to create and amend files across the filesystem. In the worse case scenario, remote code execution could be achieved.

Applications are only affected if they are using the [ChrootOS](https://pkg.go.dev/github.com/go-git/go-billy/v5/osfs#ChrootOS), which is the default when using "Plain" versions of Open and Clone funcs (e.g. PlainClone). Applications using [BoundOS](https://pkg.go.dev/github.com/go-git/go-billy/v5/osfs#BoundOS) or in-memory filesystems are not affected by this issue.
This is a `go-git` implementation issue and does not affect the upstream `git` cli.

### Patches
Users running versions of `go-git` from `v4` and above are recommended to upgrade to `v5.11` in order to mitigate this vulnerability.

### Workarounds
In cases where a bump to the latest version of `go-git` is not possible in a timely manner, we recommend limiting its use to only trust-worthy Git servers.

## Credit
Thanks to Ionut Lalu for responsibly disclosing this vulnerability to us.

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-449p-3h89-pw88
- https://nvd.nist.gov/vuln/detail/CVE-2023-49569
- https://github.com/go-git/go-git

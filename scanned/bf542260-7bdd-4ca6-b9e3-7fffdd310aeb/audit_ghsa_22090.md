# [H] LXD vulnerable to Race Condition

## Summary
Severity: High
Advisory: GHSA-8mpq-fmr3-6jxv
CVE: CVE-2015-1340
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-8mpq-fmr3-6jxv
Type: github-advisory

## Affected
- Go: `github.com/lxc/lxd` — affected >=0 <0.0.0-20151004155856-19c6961cc101

## Details
LXD before version 0.19-0ubuntu5 `doUidshiftIntoContainer()` has an unsafe `Chmod()` call that races against the stat in the `Filepath.Walk()` function. A symbolic link created in that window could cause any file on the system to have any mode of the attacker's choice.

### Specific Go Packages Affected
github.com/lxc/lxd/shared

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1340
- https://github.com/lxc/lxd/pull/1189
- https://github.com/lxc/lxd/commit/19c6961cc1012c8a529f20807328a9357f5034f4
- https://bugs.launchpad.net/ubuntu/+source/lxd/+bug/1502270
- https://github.com/lxc/lxd
- https://pkg.go.dev/vuln/GO-2021-0071

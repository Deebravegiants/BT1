# [M] Command injection in gh-ost

## Summary
Severity: Medium
Advisory: GHSA-rrp4-2xx3-mv29
CVE: CVE-2022-21687
CWE: CWE-20, CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-rrp4-2xx3-mv29
Type: github-advisory

## Affected
- Go: `github.com/github/gh-ost` — affected >=0 <1.1.3

## Details
Gh-ost version <= 1.1.2 allows users to inject DSN strings via the `-database` parameter.

This is a low severity vulnerability as the attacker must have access to the target host or trick an administrator into executing a malicious `gh-ost` command on a host running `gh-ost`, plus network access from host running `gh-ost` to the attack's malicious MySQL server.

### Impact
This issue may lead to arbitrary local file read.

### Patches
Fixed in 1.1.3+.

### Workarounds
None

### References
- https://advisory.dw1.io/51

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github/gh-ost](http://github.com/github/gh-ost)

## References
- https://github.com/github/gh-ost/security/advisories/GHSA-rrp4-2xx3-mv29
- https://nvd.nist.gov/vuln/detail/CVE-2022-21687
- https://github.com/github/gh-ost/commit/a91ab042de013cfd8fbb633763438932d9080d8f
- https://github.com/github/gh-ost

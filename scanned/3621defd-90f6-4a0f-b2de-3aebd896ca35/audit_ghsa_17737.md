# [C] go-git has an Argument Injection via the URL field

## Summary
Severity: Critical
Advisory: GHSA-v725-9546-7q7m
CVE: CVE-2025-21613
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-01-06
Source: https://github.com/advisories/GHSA-v725-9546-7q7m
Type: github-advisory

## Affected
- Go: `gopkg.in/src-d/go-git.v4` — affected >=4.0.0
- Go: `github.com/go-git/go-git/v5` — affected >=0 <5.13.0

## Details
### Impact
An argument injection vulnerability was discovered in `go-git` versions prior to `v5.13`. 

Successful exploitation of this vulnerability could allow an attacker to set arbitrary values to [git-upload-pack flags](https://git-scm.com/docs/git-upload-pack). This only happens when the `file` transport protocol is being used, as that is the only protocol that shells out to `git` binaries.

### Affected versions
Users running versions of `go-git` from `v4` and above are recommended to upgrade to `v5.13` in order to mitigate this vulnerability.

### Workarounds
In cases where a bump to the latest version of `go-git` is not possible, we recommend users to enforce restrict validation rules for values passed in the URL field.

## Credit
Thanks to @vin01 for responsibly disclosing this vulnerability to us.

## References
- https://github.com/go-git/go-git/security/advisories/GHSA-v725-9546-7q7m
- https://nvd.nist.gov/vuln/detail/CVE-2025-21613
- https://github.com/go-git/go-git

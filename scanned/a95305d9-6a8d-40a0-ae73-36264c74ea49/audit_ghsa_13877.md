# [C] go.uuid has Predictable UUID Identifiers

## Summary
Severity: Critical
Advisory: GHSA-33m6-q9v5-62r7
CVE: CVE-2021-3538
CWE: CWE-338
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-07
Source: https://github.com/advisories/GHSA-33m6-q9v5-62r7
Type: github-advisory

## Affected
- Go: `github.com/satori/go.uuid` — affected >=1.2.1-0.20180103161547-0ef6afb2f6cd <1.2.1-0.20180404165556-75cca531ea76

## Details
### CVE Description for go.uuid
A flaw was found in github.com/satori/go.uuid in versions from commit 0ef6afb2f6cdd6cdaeee3885a95099c63f18fc8c to d91630c8510268e75203009fe7daf2b8e1d60c45. Due to insecure randomness in the g.rand.Read function the generated UUIDs are predictable for an attacker.

### Update on 19 September 2024 -- This vulnerability never existed in sif

The [official NIST CVE-2021-3538 record](https://nvd.nist.gov/vuln/detail/CVE-2021-3538) says:

> A flaw was found in github.com/satori/go.uuid in versions from commit 0ef6afb2f6cdd6cdaeee3885a95099c63f18fc8c to d91630c8510268e75203009fe7daf2b8e1d60c45. 

That commit and that fix were never in a tagged release of satori/go.uuid, and prior to this announcement sif had used the last tag, 1.2.0.  The NIST record says version 1.2.0 was vulnerable, but that's not true.   So sif was never vulnerable to this.  Also, beginning with version 2.0.0, sif does not use satori/go.uuid anymore.

This update was made in response to issue #243 which has more details.

The original, incorrect sif vulnerability description is below.

-------------

### Impact

The siftool new command produces predictable UUID identifiers due to insecure randomness in the version of the `github.com/satori/go.uuid` module used as a dependency.

### Patches

A patch is available in version >= v1.2.2 of the module. Users are encouraged to upgrade.

Fixed by https://github.com/hpcng/sif/pull/90

### Workarounds

Users passing CreateInfo struct should ensure the ID field is generated using a version of github.com/satori/go.uuid that is not vulnerable to this issue. Unfortunately, the latest tagged release is vulnerable to this issue. One way to obtain a non-vulnerable version is:

`go get -u github.com/satori/go.uuid@v1.2.1-0.20180404165556-75cca531ea76`

### References

https://github.com/satori/go.uuid/issues/73

### For more information

If you have any questions or comments about this advisory:

Open an issue in https://github.com/hpcng/sif/issues

## References
- https://github.com/apptainer/sif/security/advisories/GHSA-33m6-q9v5-62r7
- https://github.com/hpcng/sif/security/advisories/GHSA-33m6-q9v5-62r7
- https://nvd.nist.gov/vuln/detail/CVE-2021-3538
- https://github.com/satori/go.uuid/issues/73
- https://github.com/satori/go.uuid/pull/75
- https://github.com/satori/go.uuid/commit/75cca531ea763666bc46e531da3b4c3b95f64557
- https://bugzilla.redhat.com/show_bug.cgi?id=1954376
- https://github.com/satori/go.uuid
- https://pkg.go.dev/vuln/GO-2022-0244
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMSATORIGOUUID-72488

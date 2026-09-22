# [H] Improper Validation of Integrity Check Value in go-tuf

## Summary
Severity: High
Advisory: GHSA-66x3-6cw3-v5gj
CVE: CVE-2022-29173
CWE: CWE-354
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-66x3-6cw3-v5gj
Type: github-advisory

## Affected
- Go: `github.com/theupdateframework/go-tuf` — affected >=0 <0.3.0

## Details
### Impact

[go-tuf](https://github.com/theupdateframework/go-tuf) does not correctly implement the [client workflow](https://theupdateframework.github.io/specification/v1.0.28/index.html#detailed-client-workflow) for updating the metadata files for roles other than the root role. Specifically, checks for rollback attacks are not implemented correctly meaning an attacker can cause clients to install software that is older than the software which the client previously knew to be available, and may include software with known vulnerabilities.

In more detail, the client code of go-tuf has several issues in regards to preventing rollback attacks:
1. It does not take into account the content of any previously trusted metadata, if available, before proceeding with updating roles other than the root role (i.e., steps 5.4.3.1 and 5.5.5 of the detailed client workflow). This means that any form of version verification done on the newly-downloaded metadata is made using the default value of zero, which always passes. 
1. For both timestamp and snapshot roles, go-tuf saves these metadata files as trusted before verifying if the version of the metafiles they refer to is correct (i.e., steps 5.5.4 and 5.6.4 of the detailed client workflow).

### Patches

A fix is available in version 0.3.0 or newer.

### Workarounds

No workarounds are known for this issue apart from upgrading.

### References

* Commit resolving the issue https://github.com/theupdateframework/go-tuf/commit/ed6788e710fc3093a7ecc2d078bf734c0f200d8d
* TUF specification version against which this vulnerability is observed is [v.1.0.28](https://theupdateframework.github.io/specification/v1.0.28/index.html#detailed-client-workflow). For more details, refer to Section 5.
* Codebase that is affected is [go-tuf@f0c3294f63b9145029464164f9bce49553b77cbb](https://github.com/theupdateframework/go-tuf/tree/f0c3294f63b9145029464164f9bce49553b77cbb)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-tuf](https://github.com/theupdateframework/go-tuf/issues)
* Email us at TUF's [mailing list](mailto:theupdateframework@googlegroups.com)
* The [#tuf](https://cloud-native.slack.com/archives/C8NMD3QJ3) channel on [CNCF Slack](https://slack.cncf.io/).

## References
- https://github.com/theupdateframework/go-tuf/security/advisories/GHSA-66x3-6cw3-v5gj
- https://nvd.nist.gov/vuln/detail/CVE-2022-29173
- https://github.com/theupdateframework/go-tuf/commit/ed6788e710fc3093a7ecc2d078bf734c0f200d8d
- https://github.com/theupdateframework/go-tuf
- https://pkg.go.dev/vuln/GO-2022-0444

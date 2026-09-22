# [H] OpenFGA Authorization Bypass

## Summary
Severity: High
Advisory: GHSA-m3q4-7qmj-657m
CVE: CVE-2022-23542
CWE: CWE-285
Ecosystem: Go
Published: 2022-12-20
Source: https://github.com/advisories/GHSA-m3q4-7qmj-657m
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0.3.0 <0.3.1

## Details
### Overview
During our internal security assessment, it was discovered that OpenFGA versions v0.3.0 is vulnerable to authorization bypass under certain conditions.

### Am I Affected?
You are affected by this vulnerability if **all** of the following applies:

1.  You are using OpenFGA v0.3.0
2. You created a model using modeling language v1.1 that applies a type restriction to an object e.g. `define viewer: [user]`
3. You created tuples based on the aforementioned model, e.g. `document:1#viewer@user:jon`
4. You updated the previous model by adding a new type and replacing the previous restriction with the newly added type e.g. `define viewer: [employee]`
5. You use the tuples created against the first model (step 3) and issue checks against the updated model e.g. `user=user:jon, relation=viewer, object:document:1`

### How to fix that?
Upgrade to version v0.3.1

### Backward Compatibility
This update is backward compatible.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-m3q4-7qmj-657m
- https://nvd.nist.gov/vuln/detail/CVE-2022-23542
- https://github.com/openfga/openfga/pull/422
- https://github.com/openfga/openfga
- https://github.com/openfga/openfga/releases/tag/v0.3.1

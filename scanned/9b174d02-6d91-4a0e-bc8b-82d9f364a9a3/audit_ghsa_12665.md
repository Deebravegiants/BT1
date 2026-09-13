# [M] OpenFGA vulnerable to denial of service due to circular relationship

## Summary
Severity: Medium
Advisory: GHSA-hr9r-8phq-5x8j
CVE: CVE-2023-35933
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-28
Source: https://github.com/advisories/GHSA-hr9r-8phq-5x8j
Type: github-advisory

## Affected
- Go: `github.com/openfga/openfga` — affected >=0 <1.1.1

## Details
### Overview

OpenFGA versions v1.1.0 and prior are vulnerable to a DoS attack when certain Check and ListObjects calls are executed against authorization models that contain circular relationship definitions.

### Am I Affected?

You are affected by this vulnerability if you are using OpenFGA v1.1.0 or earlier, and if you are executing certain [Check](https://openfga.dev/api/service#/Relationship%20Queries/Check) or [ListObjects](https://openfga.dev/api/service#/Relationship%20Queries/ListObjects) calls against a vulnerable authorization model. To see which of your models could be vulnerable to this attack, download OpenFGA v1.2.0 and run the following command: 

```
./openfga validate-models --datastore-engine <ENGINE> --datastore-uri <URI> | jq .[] | select(.Error | contains("loop"))
```

replacing the variables `<ENGINE>` and `<URI>` as needed.

### Fix

Upgrade to v1.1.1.

### Backward Compatibility

If you are not passing an invalid authorization model (as identified by running `./openfga validate-models`) as a parameter of your Check and ListObjects calls, this upgrade is backwards compatible. 

Otherwise, OpenFGA v1.1.1 will start returning HTTP 400 status codes on those calls.

## References
- https://github.com/openfga/openfga/security/advisories/GHSA-hr9r-8phq-5x8j
- https://nvd.nist.gov/vuln/detail/CVE-2023-35933
- https://github.com/openfga/openfga/commit/087ce392595f3c319ab3028b5089118ea4063452
- https://github.com/openfga/openfga
- https://openfga.dev/api/service#/Relationship%20Queries/Check
- https://openfga.dev/api/service#/Relationship%20Queries/ListObjects

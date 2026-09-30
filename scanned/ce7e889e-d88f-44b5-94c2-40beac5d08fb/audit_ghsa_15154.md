# [M] CubeFS leaks magic secret key when starting Blobstore access service

## Summary
Severity: Medium
Advisory: GHSA-8h2x-gr2c-c275
CVE: CVE-2023-46741
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-8h2x-gr2c-c275
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0 <3.3.1

## Details
A vulnerability was found in CubeFS that could allow users to read sensitive data from the logs which could allow them escalate privileges. 

CubeFS leaks configuration keys in plaintext format in the logs. These keys could allow anyone to carry out operations on blobs that they otherwise do not have permissions for. For example, an attacker that has succesfully retrieved a secret key from the logs can delete blogs from the blob store.

The attacker can either be an internal user with limited privileges to read the log, or it can be an external user who has escalated privileges sufficiently to access the logs. There is no evidence of this vulnerability being exploited in the wild. It was found during an ongoing security audit carried out by [Ada Logics](https://adalogics.com/) in collaboration with [OSTIF](https://ostif.org/) and the [CNCF](https://www.cncf.io/).

The vulnerability has been patched in v3.3.1. There is no other mitigated than upgrading.

## References
- https://github.com/cubefs/cubefs/security/advisories/GHSA-8h2x-gr2c-c275
- https://nvd.nist.gov/vuln/detail/CVE-2023-46741
- https://github.com/cubefs/cubefs/commit/972f0275ee8d5dbba4b1530da7c145c269b31ef5
- https://github.com/cubefs/cubefs

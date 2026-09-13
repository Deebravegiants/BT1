# [H] Authenticated users can crash the CubeFS servers with maliciously crafted requests

## Summary
Severity: High
Advisory: GHSA-qc6v-g3xw-grmx
CVE: CVE-2023-46738
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-qc6v-g3xw-grmx
Type: github-advisory

## Affected
- Go: `github.com/cubefs/cubefs` — affected >=0 <3.3.1

## Details
A security vulnerability was found in CubeFS HandlerNode that could allow authenticated users to send maliciously-crafted requests that would crash the ObjectNode and deny other users from using it. The root cause was improper handling of incoming HTTP requests that could allow an attacker to control the ammount of memory that the ObjectNode would allocate. A malicious request could make the ObjectNode allocate more memory that the machine had available, and the attacker could exhaust memory by way of a single malicious request.

An attacker would need to be authenticated in order to invoke the vulnerable code with their malicious request and have permissions to delete objects. In addition, the attacker would need to know the names of existing buckets of the CubeFS deployment - otherwise the request would be rejected before it reached the vulnerable code. As such, the most likely attacker is an inside user or an attacker that has breached the account of an existing user in the cluster. There is no evidence of this attack being exploited in the wild. The vulnerability was found during a security audit carried out by [Ada Logics](https://adalogics.com/) in collaboration with [OSTIF](https://ostif.org/) and the [CNCF](https://www.cncf.io/).

The issue has been patched in v3.3.1. There is no other mitigation besides upgrading.

## References
- https://github.com/cubefs/cubefs/security/advisories/GHSA-qc6v-g3xw-grmx
- https://nvd.nist.gov/vuln/detail/CVE-2023-46738
- https://github.com/cubefs/cubefs/commit/dd46c24873c8f3df48d0a598b704ef9bd24b1ec1
- https://github.com/cubefs/cubefs

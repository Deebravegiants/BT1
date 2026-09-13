# [M] S3Proxy allows insecure path traversal in filesystem and filesystem-nio2 storage backends

## Summary
Severity: Medium
Advisory: GHSA-2ccp-vqmv-4r4x
CVE: CVE-2025-24961
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-03
Source: https://github.com/advisories/GHSA-2ccp-vqmv-4r4x
Type: github-advisory

## Affected
- Maven: `org.gaul:s3proxy` — affected >=0 <2.6.0

## Details
### Impact
Users of the filesystem and filesystem-nio2 storage backends could unintentionally expose local files to authenticated clients.

### Patches
Upgrade to S3Proxy 2.6.0 which includes apache/jclouds@b0819e0ef5e08c792a4d1724b938714ce9503aa3 and 86b6ee4749aa163a78e7898efc063617ed171980.

### Workarounds
None

### References
Privately reported by XBOW Team @xbow-security.

## References
- https://github.com/gaul/s3proxy/security/advisories/GHSA-2ccp-vqmv-4r4x
- https://nvd.nist.gov/vuln/detail/CVE-2025-24961
- https://github.com/apache/jclouds/commit/b0819e0ef5e08c792a4d1724b938714ce9503aa3
- https://github.com/gaul/s3proxy/commit/86b6ee4749aa163a78e7898efc063617ed171980
- https://github.com/gaul/s3proxy

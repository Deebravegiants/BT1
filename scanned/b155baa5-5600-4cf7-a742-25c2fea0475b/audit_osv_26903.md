# [M] Eclipse OpenJ9 possible infinite busy hang

## Summary
Severity: Medium
Advisory: CVE-2023-5676
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-15
Source: https://osv.dev/vulnerability/CVE-2023-5676
Type: osv

## Details
In Eclipse OpenJ9 before version 0.41.0, the JVM can be forced into an infinite busy hang on a spinlock or a segmentation fault if a shutdown signal (SIGTERM, SIGINT or SIGHUP) is received before the JVM has finished initializing.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5676.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5676
- https://security.netapp.com/advisory/ntap-20241108-0002/
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/13
- https://github.com/eclipse-openj9/openj9/pull/18085

# [H] Path traversal in ServiceCenter

## Summary
Severity: High
Advisory: GHSA-x6jv-5vfg-gm7x
CVE: CVE-2021-21501
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-x6jv-5vfg-gm7x
Type: github-advisory

## Affected
- Go: `github.com/apache/servicecomb-service-center` — affected >=0 <2.0.0

## Details
Improper configuration will cause ServiceComb ServiceCenter Directory Traversal problem in ServcieCenter 1.x.x versions and fixed in 2.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21501
- https://github.com/apache/servicecomb-service-center/pull/788
- https://github.com/apache/servicecomb-service-center/commit/f4f44fe5d4a7e530ca8ee7c6f2c9e891ae8353c9
- https://github.com/apache/servicecomb-service-center
- https://lists.apache.org/thread.html/r337be65e504eac52a12e89d7de40345e5d335deee9dd7288f7f59b81%40%3Cdev.servicecomb.apache.org%3E
- http://www.openwall.com/lists/oss-security/2021/08/10/3

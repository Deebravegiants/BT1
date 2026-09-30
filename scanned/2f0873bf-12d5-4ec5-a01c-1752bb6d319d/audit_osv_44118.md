# [C] Alluxio through 2.9.5 S3 REST Proxy Authentication Bypass via Unverified Request Signature

## Summary
Severity: Critical
Advisory: CVE-2026-79787
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79787
Type: osv

## Details
Alluxio's S3 REST proxy fails to verify AWS Signature Version 4 signatures in its default configuration, allowing unauthenticated attackers to spoof user identity. Attackers can extract usernames from unsigned Authorization headers and impersonate any user, including service accounts, to read, write, and delete arbitrary data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79787.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-79787
- https://www.vulncheck.com/advisories/alluxio-through-2.9.5-s3-rest-proxy-authentication-bypass-via-unverified-request-signature
- https://github.com/Alluxio/alluxio/issues/18755
- https://github.com/Alluxio/alluxio
- https://github.com/Alluxio/alluxio/blob/v2.9.5/core/server/proxy/src/main/java/alluxio/proxy/s3/S3RestUtils.java

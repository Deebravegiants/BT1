# [M] CVE-2026-71191

## Summary
Severity: Medium
Advisory: CVE-2026-71191
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71191
Type: osv

## Details
In OpenStack Swift through 2.38.0, S3API middleware does not enforce that semantic x-amz-* headers are covered by the SigV4 signature on presigned URL requests. An attacker who obtains a presigned PUT URL can inject an unsigned X-Amz-Copy-Source header, causing Swift to perform a server-side copy from an arbitrary source object using the signer's authorization context. The attacker can read any object the signer has access to, provided the target project_id, container name, and object name are known. This affects all deployments using the default s3_acl=false configuration.

## References
- https://opendev.org/openstack/swift
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71191.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71191
- https://openwall.com/lists/oss-security/2026/07/28/26
- https://security.openstack.org/ossa/OSSA-2026-030.html
- https://launchpad.net/bugs/2158733

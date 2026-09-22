# [M] CVE-2026-71192

## Summary
Severity: Medium
Advisory: CVE-2026-71192
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71192
Type: osv

## Details
In OpenStack Swift through 2.38.0, the S3API middleware does not sanitize Swift-native control headers (X-Copy-From, X-Copy-From-Account) from S3 API requests when s3_acl=true. An
attacker can inject these headers into a signed PUT request targeting their own bucket, causing Swift to perform a server-side copy from another tenant's private object. The source object authorization is bypassed because the S3API middleware has already authorized the request against the destination. The attacker can read any object whose project_id, container name, and object name are known, regardless of the source object's ACLs or ownership. This requires the non-default s3_acl=true configuration.

## References
- https://opendev.org/openstack/swift
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71192.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71192
- https://openwall.com/lists/oss-security/2026/07/28/26
- https://security.openstack.org/ossa/OSSA-2026-030.html
- https://launchpad.net/bugs/2158733

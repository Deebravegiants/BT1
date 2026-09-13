# [M] Red hat a-mq streams: component version with information disclosure flaw

## Summary
Severity: Medium
Advisory: CVE-2023-0833
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-0833
Type: osv

## Details
A flaw was found in Red Hat's AMQ-Streams, which ships a version of the OKHttp component with an information disclosure flaw via an exception triggered by a header containing an illegal value. This issue could allow an authenticated attacker to access information outside of their regular permissions.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://access.redhat.com/errata/RHSA-2023:1241
- https://access.redhat.com/errata/RHSA-2023:3223
- https://access.redhat.com/security/cve/CVE-2023-0833
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0833.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0833
- https://bugzilla.redhat.com/show_bug.cgi?id=2169845
- https://github.com/square/okhttp/issues/6738
- https://github.com/square/okhttp

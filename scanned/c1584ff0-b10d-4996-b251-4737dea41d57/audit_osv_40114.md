# [M] Apache CXF: XML External Entity (XXE) Injection in W3CMultiSchemaFactory and EndpointReferenceUtils

## Summary
Severity: Medium
Advisory: CVE-2026-49875
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-49875
Type: osv

## Details
Apache CXF's EndpointReferenceUtils and W3CMultiSchemaFactory classes construct a SAXParserFactory without the necessary JAXP hardening configurations, enabling out-of-band (OOB) 
external entity resolution. Users are recommended to upgrade to versions 4.2.2 or 4.1.7 or 3.6.12, which fix this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/11/2
- https://repo.maven.apache.org/maven2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-49875.json
- https://access.redhat.com/errata/RHSA-2026:36839
- https://access.redhat.com/errata/RHSA-2026:37390
- https://access.redhat.com/security/cve/CVE-2026-49875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49875.json
- https://lists.apache.org/thread/3kb9w5bg90xcp06fccoz9k3gpsvyy79o
- https://nvd.nist.gov/vuln/detail/CVE-2026-49875
- https://bugzilla.redhat.com/show_bug.cgi?id=2488309

# [M] Foreman: world readable file containing secrets

## Summary
Severity: Medium
Advisory: CVE-2023-4886
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-03
Source: https://osv.dev/vulnerability/CVE-2023-4886
Type: osv

## Details
A sensitive information exposure vulnerability was found in foreman. Contents of tomcat's server.xml file, which contain passwords to candlepin's keystore and truststore, were found to be world readable.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2023:7851
- https://access.redhat.com/errata/RHSA-2024:1061
- https://access.redhat.com/security/cve/CVE-2023-4886
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4886.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4886
- https://bugzilla.redhat.com/show_bug.cgi?id=2230135

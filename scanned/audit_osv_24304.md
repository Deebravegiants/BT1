# [H] MGT-COMMERCE CloudPanel Shared Certificate

## Summary
Severity: High
Advisory: CVE-2023-0391
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-21
Source: https://osv.dev/vulnerability/CVE-2023-0391
Type: osv

## Details
MGT-COMMERCE CloudPanel ships with a static SSL certificate to encrypt communications to the administrative interface, shared across every installation of CloudPanel. This behavior was observed in version 2.2.0. There has been no indication from the vendor this has been addressed in version 2.2.1.

## References
- https://www.bleepingcomputer.com/news/security/cloudpanel-installations-use-the-same-ssl-certificate-private-key/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0391.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0391
- https://www.rapid7.com/blog/post/2023/03/21/cve-2023-0391-mgt-commerce-cloudpanel-shared-certificate-vulnerability-and-weak-installation-procedures/

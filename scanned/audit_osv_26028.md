# [M] Stackrox: missing http security headers allows for clickjacking in web ui

## Summary
Severity: Medium
Advisory: CVE-2023-4958
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:L)
Published: 2023-12-12
Source: https://osv.dev/vulnerability/CVE-2023-4958
Type: osv

## Details
In Red Hat Advanced Cluster Security (RHACS), it was found that some security related HTTP headers were missing, allowing an attacker to exploit this with a clickjacking attack. An attacker could exploit this by convincing a valid RHACS user to visit an attacker-controlled web page, that deceptively points to valid RHACS endpoints, hijacking the user's account permissions to perform other actions.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2023:5206
- https://access.redhat.com/security/cve/CVE-2023-4958
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4958.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4958
- https://bugzilla.redhat.com/show_bug.cgi?id=1990363

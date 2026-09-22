# [M] Memory leak on tls connections

## Summary
Severity: Medium
Advisory: CVE-2022-4132
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2022-4132
Type: osv

## Details
A flaw was found in JSS. A memory leak in JSS requires non-standard configuration but is a low-effort DoS vector if configured that way (repeatedly hitting the login page).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2022-4132
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4132.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4132
- https://bugzilla.redhat.com/show_bug.cgi?id=2147372

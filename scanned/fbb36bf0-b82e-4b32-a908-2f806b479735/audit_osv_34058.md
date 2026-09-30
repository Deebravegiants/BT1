# [M] Rhdh: red hat developer hub user permissions

## Summary
Severity: Medium
Advisory: CVE-2025-5417
CVSS: 6.1 (CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-5417
Type: osv

## Details
An insufficient access control vulnerability was found in the Red Hat
Developer Hub rhdh/rhdh-hub-rhel9 container image. The Red Hat Developer Hub cluster admin/user, who has standard user access to the cluster, and the Red Hat Developer Hub namespace, can access the
rhdh/rhdh-hub-rhel9 container image and modify the image's content. This issue affects the confidentiality and integrity of the data, and any changes made are not permanent, as they reset after the pod restarts.

## References
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2025:14090
- https://access.redhat.com/security/cve/CVE-2025-5417
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/5xxx/CVE-2025-5417.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-5417
- https://bugzilla.redhat.com/show_bug.cgi?id=2369602
- https://github.com/redhat-developer/rhdh

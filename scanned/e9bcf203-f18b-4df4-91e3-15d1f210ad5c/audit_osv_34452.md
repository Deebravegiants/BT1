# [M] Rhacm: users with clusterreader role can see credentials from managed-clusters

## Summary
Severity: Medium
Advisory: CVE-2025-6017
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2025-6017
Type: osv

## Details
A flaw was found in Red Hat Advanced Cluster Management through versions 2.10, before 2.10.7, 2.11, before 2.11.4, and 2.12, before 2.12.4. This vulnerability allows an unprivileged user to view confidential managed cluster credentials through the UI. This information should only be accessible to authorized users and may result in the loss of confidentiality of administrative information, which could be leaked to unauthorized actors.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-6017
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6017.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6017
- https://bugzilla.redhat.com/show_bug.cgi?id=2372362
- https://github.com/open-cluster-management-io/ocm

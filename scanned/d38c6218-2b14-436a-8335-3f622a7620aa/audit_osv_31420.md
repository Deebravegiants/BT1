# [C] Openshift-ai: overly permissive clusterrole allows authenticated users to escalate privileges to cluster admin

## Summary
Severity: Critical
Advisory: CVE-2025-10725
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-09-30
Source: https://osv.dev/vulnerability/CVE-2025-10725
Type: osv

## Details
A flaw was found in Red Hat Openshift AI Service. A low-privileged attacker with access to an authenticated account, for example as a data scientist using a standard Jupyter notebook, can escalate their privileges to a full cluster administrator. This allows for the complete compromise of the cluster's confidentiality, integrity, and availability. The attacker can steal sensitive data, disrupt all services, and take control of the underlying infrastructure, leading to a total breach of the platform and all applications hosted on it.

## References
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2025:16981
- https://access.redhat.com/errata/RHSA-2025:16982
- https://access.redhat.com/errata/RHSA-2025:16983
- https://access.redhat.com/errata/RHSA-2025:16984
- https://access.redhat.com/errata/RHSA-2025:17501
- https://access.redhat.com/security/cve/CVE-2025-10725
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10725.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10725
- https://bugzilla.redhat.com/show_bug.cgi?id=2396641
- https://github.com/opendatahub-io/opendatahub-operator/commit/070057ebd0882be0e397bee1daa18c36374a03c0
- https://github.com/opendatahub-io/opendatahub-operator/pull/2571
- https://github.com/opendatahub-io/opendatahub-operator

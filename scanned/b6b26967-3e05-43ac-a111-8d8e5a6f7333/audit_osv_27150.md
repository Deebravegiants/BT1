# [H] Cluster-monitoring-operator: credentials leak

## Summary
Severity: High
Advisory: CVE-2024-1139
Aliases: GHSA-x5m7-63c6-fx79, GO-2024-2789
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-1139
Type: osv

## Details
A credentials leak vulnerability was found in the cluster monitoring operator in OCP.  This issue may allow a remote attacker who has basic login credentials to check the pod manifest to discover a repository pull secret.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/errata/RHSA-2024:1887
- https://access.redhat.com/errata/RHSA-2024:1891
- https://access.redhat.com/errata/RHSA-2024:2047
- https://access.redhat.com/errata/RHSA-2024:2782
- https://access.redhat.com/security/cve/CVE-2024-1139
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1139.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1139
- https://bugzilla.redhat.com/show_bug.cgi?id=2262158
- https://github.com/openshift/cluster-monitoring-operator

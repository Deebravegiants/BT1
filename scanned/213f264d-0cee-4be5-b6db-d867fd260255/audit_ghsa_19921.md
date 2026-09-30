# [M] OpenShift Hive Has an Uncontrolled Resource Consumption Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c392-wrgw-jjfw
CVE: CVE-2024-25132
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-c392-wrgw-jjfw
Type: github-advisory

## Affected
- Go: `github.com/openshift/hive` — affected >=0

## Details
A flaw was found in the Hive hibernation controller component of OpenShift Dedicated. The ClusterDeployment.hive.openshift.io/v1 resource can be created with the spec.installed field set to true, regardless of the installation status, and a positive timespan for the spec.hibernateAfter value. If a ClusterSync.hiveinternal.openshift.io/v1alpha1 resource is also created, the hive hibernation controller will enter the reconciliation loop leading to a panic when accessing a non-existing field in the ClusterDeployment’s status section, resulting in a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-25132
- https://access.redhat.com/security/cve/CVE-2024-25132
- https://bugzilla.redhat.com/show_bug.cgi?id=2260371
- https://github.com/openshift/hive

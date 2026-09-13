# [M] Assisted-service: assisted-service: authenticated users can gain administrative access to openshift clusters via credential disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-7163
CVSS: 6.1 (CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/CVE-2026-7163
Type: osv

## Details
A vulnerability in the assisted-service REST API, an optional Assisted Installer (assisted-service) component in the Multicluster Engine (MCE), allows an authenticated user with minimal namespace-scoped privileges to obtain administrative credentials for arbitrary clusters provisioned through the hub. 

The credentials download endpoint (GET /v2/clusters/{cluster_id}/credentials, which returns the kubeadmin password) and the kubeconfig download endpoint are operational in AUTH_TYPE=local mode, the only authentication mode available in on-premises ACM/MCE hub deployments. The local authenticator unconditionally grants full administrative access to any request bearing a valid JWT, with no per-endpoint restrictions. A valid local JWT is embedded as a plaintext query parameter in InfraEnvStatus.ISODownloadURL and is readable by any user who has get rights on an InfraEnv object in their own namespace.

The affected components ship as part of Multicluster Engine (MCE). The Red Hat Advanced Cluster Management (ACM) deployments that include MCE are equally affected.
This issue does not affect the hosted SaaS offering (console.redhat.com), which uses a different authentication mode.

Successful exploitation gives the attacker the kubeadmin password and kubeconfig for any OpenShift cluster provisioned through the affected hub, granting unrestricted root-level administrative access to those spoke clusters.

## References
- https://catalog.redhat.com/software/containers/
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-7163.json
- https://access.redhat.com/errata/RHSA-2026:11511
- https://access.redhat.com/errata/RHSA-2026:11512
- https://access.redhat.com/errata/RHSA-2026:12116
- https://access.redhat.com/errata/RHSA-2026:12337
- https://access.redhat.com/errata/RHSA-2026:18584
- https://access.redhat.com/errata/RHSA-2026:18585
- https://access.redhat.com/security/cve/CVE-2026-7163
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/7xxx/CVE-2026-7163.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-7163
- https://bugzilla.redhat.com/show_bug.cgi?id=2463152
- https://github.com/openshift/assisted-service

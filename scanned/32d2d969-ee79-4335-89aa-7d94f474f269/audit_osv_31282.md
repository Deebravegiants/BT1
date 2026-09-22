# [H] Odh-dashboard: odh-model-controller: cross-model authentication bypass in openshift ai

## Summary
Severity: High
Advisory: CVE-2024-7557
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/CVE-2024-7557
Type: osv

## Details
A vulnerability was found in OpenShift AI that allows for authentication bypass and privilege escalation across models within the same namespace. When deploying AI models, the UI provides the option to protect models with authentication. However, credentials from one model can be used to access other models and APIs within the same namespace. The exposed ServiceAccount tokens, visible in the UI, can be utilized with oc --token={token} to exploit the elevated view privileges associated with the ServiceAccount, leading to unauthorized access to additional resources.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://access.redhat.com/security/cve/CVE-2024-7557
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7557.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7557
- https://bugzilla.redhat.com/show_bug.cgi?id=2303094
- https://github.com/opendatahub-io/odh-dashboard/pull/3198
- https://github.com/opendatahub-io/odh-dashboard

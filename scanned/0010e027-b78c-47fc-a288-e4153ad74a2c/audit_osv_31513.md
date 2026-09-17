# [M] Terraform Enterprise state versions can be created by users with specific permissions without sufficient write access

## Summary
Severity: Medium
Advisory: CVE-2025-13432
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-11-21
Source: https://osv.dev/vulnerability/CVE-2025-13432
Type: osv

## Details
Terraform state versions can be created by a user with specific but insufficient permissions in a Terraform Enterprise workspace. This may allow for the alteration of infrastructure if a subsequent plan operation is approved by a user with approval permission or auto-applied. This vulnerability, CVE-2025-13432, is fixed in Terraform Enterprise version 1.1.1 and 1.0.3.

## References
- https://discuss.hashicorp.com/t/hcsec-2025-34-terraform-enterprise-state-versions-can-be-created-by-users-without-sufficient-write-access/76821
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13432.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-13432

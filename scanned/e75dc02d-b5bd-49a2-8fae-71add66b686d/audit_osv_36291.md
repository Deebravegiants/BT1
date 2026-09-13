# [C] vCluster Platform's Access Keys Allows Access Beyond Scope

## Summary
Severity: Critical
Advisory: CVE-2026-22806
Aliases: GHSA-c539-w4ch-7wxq
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-29
Source: https://osv.dev/vulnerability/CVE-2026-22806
Type: osv

## Details
vCluster Platform provides a Kubernetes platform for managing virtual clusters, multi-tenancy, and cluster sharing. Prior to versions 4.6.0, 4.5.4, 4.4.2, and 4.3.10, when an access key is created with a limited scope, the scope can be bypassed to access resources outside of it. However, the user still cannot access resources beyond what is accessible to the owner of the access key. Versions 4.6.0, 4.5.4, 4.4.2, and 4.3.10 fix the vulnerability. Some other mitigations are available. Users can limit exposure by reviewing access keys which are scoped and ensuring any users with access to them have appropriate permissions set. Creating automation users with very limited permissions and using access keys for these automation users can be used as a temporary workaround where upgrading is not immediately possible but scoped access keys are needed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22806.json
- https://github.com/loft-sh/loft/security/advisories/GHSA-c539-w4ch-7wxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-22806

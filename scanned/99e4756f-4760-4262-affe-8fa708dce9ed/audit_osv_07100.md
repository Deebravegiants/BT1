# [M] Apache NiFi: Missing Complete Authorization for Parameter and Service References

## Summary
Severity: Medium
Advisory: BIT-nifi-2024-56512
Aliases: CVE-2024-56512, GHSA-mpj7-7mg7-x95j
Ecosystem: Bitnami
Published: 2025-09-12
Source: https://osv.dev/vulnerability/BIT-nifi-2024-56512
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.10.0 <2.1.0

## Details
Apache NiFi 1.10.0 through 2.0.0 are missing fine-grained authorization checking for Parameter Contexts, referenced Controller Services, and referenced Parameter Providers, when creating new Process Groups.

Creating a new Process Group can include binding to a Parameter Context, but in cases where the Process Group did not reference any Parameter values, the framework did not check user authorization for the bound Parameter Context. Missing authorization for a bound Parameter Context enabled clients to download non-sensitive Parameter values after creating the Process Group.

Creating a new Process Group can also include referencing existing Controller Services or Parameter Providers. The framework did not check user authorization for referenced Controller Services or Parameter Providers, enabling clients to create Process Groups and use these components that were otherwise unauthorized.

This vulnerability is limited in scope to authenticated users authorized to create Process Groups. The scope is further limited to deployments with component-based authorization policies. Upgrading to Apache NiFi 2.1.0 is the recommended mitigation, which includes authorization checking for Parameter and Controller Service references on Process Group creation.

## References
- http://www.openwall.com/lists/oss-security/2024/12/28/1
- https://lists.apache.org/thread/cjc8fns5kjsho0s7vonlnojokyfx47wn
- https://nvd.nist.gov/vuln/detail/CVE-2024-56512

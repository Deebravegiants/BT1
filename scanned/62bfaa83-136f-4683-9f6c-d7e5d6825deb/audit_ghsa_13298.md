# [C] Orchid Deserialization of Untrusted Data vulnerability leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-ph6g-p72v-pc3p
CVE: CVE-2023-36825
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-11
Source: https://github.com/advisories/GHSA-ph6g-p72v-pc3p
Type: github-advisory

## Affected
- Packagist: `orchid/platform` — affected >=14.0.0-alpha4 <14.5.0

## Details
Orchid is a Laravel package that allows application development of back-office applications, admin/user panels, and dashboards.

### Impact

A vulnerability present starting in version 14.0.0-alpha4 and prior to version 14.5.0 is related to the deserialization of untrusted data from the `_state` query parameter, which can result in remote code execution. This vulnerability is related to the deserialization of untrusted data from the `_state` query parameter, which can result in remote code execution.

### Patches

The issue has been addressed in version 14.5.0. Users are advised to upgrade their software to this version or any subsequent versions that include the patch. There are no known workarounds.

### Workarounds

In this case, it is recommended for users to upgrade to the patched version rather than relying on workarounds. Upgrading to the fixed version ensures that the vulnerability is no longer present and provides the best protection against remote code execution

### References

For more detailed information about this workaround and its effectiveness, users should consult the support channels provided by the software or system developer. They can provide specific guidance on implementing this workaround and any potential limitations or caveats associated with it.

----

This vulnerability was discovered by Vladislav Gladkiy (Positive Technologies)

## References
- https://github.com/orchidsoftware/platform/security/advisories/GHSA-ph6g-p72v-pc3p
- https://nvd.nist.gov/vuln/detail/CVE-2023-36825
- https://github.com/orchidsoftware/platform
- https://github.com/orchidsoftware/platform/releases/tag/14.5.0

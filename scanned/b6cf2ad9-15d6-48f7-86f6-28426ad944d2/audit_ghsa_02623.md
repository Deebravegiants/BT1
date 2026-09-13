# [M] YAML deserialization can run untrusted code

## Summary
Severity: Medium
Advisory: GHSA-q4rf-3fhx-88pf
CVE: CVE-2021-39132
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-q4rf-3fhx-88pf
Type: github-advisory

## Affected
- Maven: `org.rundeck:rundeck-core` — affected >=3.4.0 <3.4.3
- Maven: `org.rundeck:rundeck-core` — affected >=0 <3.3.14

## Details
### Impact

An authorized user can upload a zip-format plugin with a crafted plugin.yaml, or a crafted aclpolicy yaml file, or upload an untrusted project archive with a crafted aclpolicy yaml file, that can cause the server to run untrusted code on Rundeck Community or Enterprise Edition.  An authenticated user can make a POST request, that can cause the server to run untrusted code on Rundeck Enterprise Edition.

The zip-format plugin issues requires authentication and authorization to these access levels, and affects all Rundeck editions:

* `admin` level access to the `system` resource type

The ACL Policy yaml file upload issues requires authentication and authorization to these access levels, and affects all Rundeck editions: 

* `create` `update` or `admin` level access to a `project_acl` resource
* `create` `update` or `admin` level access to the `system_acl` resource

The unauthorized POST request requires authentication, but no specific authorization, and affects Rundeck Enterprise only.

### Patches
Versions 3.4.3, 3.3.14

### Workarounds

Please visit [https://rundeck.com/security](https://rundeck.com/security) for information about specific workarounds.

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@rundeck.com](mailto:security@rundeck.com)

To report security issues to Rundeck please use the form at [https://rundeck.com/security](https://rundeck.com/security)

Reporter: Rojan Rijal from Tinder Red Team

## References
- https://github.com/rundeck/rundeck/security/advisories/GHSA-q4rf-3fhx-88pf
- https://nvd.nist.gov/vuln/detail/CVE-2021-39132
- https://github.com/rundeck/rundeck/commit/850d12e21d22833bc148b7f458d7cb5949f829b6
- https://github.com/rundeck/rundeck

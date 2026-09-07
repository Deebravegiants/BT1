# [H] Write access to the catalog for any user when restricted-admin role is enabled in Rancher

## Summary
Severity: High
Advisory: GHSA-hx8w-ghh8-r4xf
CVE: CVE-2021-4200
CWE: CWE-269, CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2022-05-02
Source: https://github.com/advisories/GHSA-hx8w-ghh8-r4xf
Type: github-advisory

## Affected
- Go: `github.com/rancher/rancher` — affected >=2.6.0 <2.6.4
- Go: `github.com/rancher/rancher` — affected >=2.5.0 <2.5.13

## Details
### Impact

This vulnerability only affects customers using the [`restricted-admin`](https://rancher.com/docs/rancher/v2.6/en/admin-settings/rbac/global-permissions/#restricted-admin) role in Rancher. For this role to be active, Rancher must be bootstrapped with the environment variable `CATTLE_RESTRICTED_DEFAULT_ADMIN=true` or the configuration flag `restrictedAdmin=true`.

A flaw was discovered in Rancher versions from 2.5.0 up to and including 2.5.12 and from 2.6.0 up to and including 2.6.3 where the `global-data` role in `cattle-global-data` namespace grants write access to the Catalogs. Since each user with any level of catalog access was bound to the `global-data` role, this grants write access to templates (`CatalogTemplates`) and template versions (`CatalogTemplateVersions`) for any user with any level of catalog access. New users created in Rancher are by default assigned to the `user` role (standard user), which is not designed to grant write catalog access. This vulnerability effectively elevates the privilege of any user to write access for the catalog template and catalog template version resources.

A malicious user could abuse this vulnerability to:

1. Make applications or individual versions of applications visible or hidden on the UI, by modifying `version` and `rancherMaxVersion` fields.
2. Change the logo (field `icon`) of an application or template to an arbitrary image.
3. Make a chart appear as a trusted or partner chart. This can be abused to make less trusted charts, such as customer defined charts, appear more legitimate than they are, by adding the label `io.rancher.certified: partner`.
4. Swap template versions between templates of charts inside the same catalog. This can be exploited to swap the files from one chart or version to another, by changing `versionDir` field. When a user on the target cluster deploys their chart, it will deploy the modified version.

This vulnerability does not allow to modify the base64 encoded `files` fields of the `templateVersions`, so one cannot inject arbitrary data to charts that have already been pulled from their respective catalog.

Without access to the Catalog, malicious users are limited to injecting apps which already exist in a registered catalog. They would need write access to the catalog or external write access to a source repo to inject arbitrary code.

### Patches
Patched versions include releases 2.5.13, 2.6.4 and later versions.

### Workarounds
Limit access in Rancher to trusted users. There is not a direct mitigation besides upgrading to the patched Rancher versions.

**Note:** If you use the `restricted-admin` as the default admin role in your environment, it's highly advised to review `CatalogTemplates` and `CatalogTemplateVersions` for possible malicious modifications.

### For more information
If you have any questions or comments about this advisory:
* Reach out to [SUSE Rancher Security team](https://github.com/rancher/rancher/security/policy) for security related inquiries.
* Open an issue in [Rancher](https://github.com/rancher/rancher/issues/new/choose) repository.
* Verify our [support matrix](https://www.suse.com/suse-rancher/support-matrix/all-supported-versions/) and [product support lifecycle](https://www.suse.com/lifecycle/).

## References
- https://github.com/rancher/rancher/security/advisories/GHSA-hx8w-ghh8-r4xf
- https://nvd.nist.gov/vuln/detail/CVE-2021-4200
- https://bugzilla.suse.com/show_bug.cgi?id=1193992
- https://rancher.com/docs/rancher/v2.6/en/admin-settings/rbac/global-permissions/#restricted-admin
- github.com/rancher/rancher

# [C] UmbracoForms Vulnerable to Remote Code Execution via Untrusted WSDL Compilation in Dynamic SOAP Client Generation

## Summary
Severity: Critical
Advisory: GHSA-vrgw-pc9c-qrrc
CVE: CVE-2025-68924
CWE: CWE-502, CWE-829, CWE-915, CWE-94
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-vrgw-pc9c-qrrc
Type: github-advisory

## Affected
- NuGet: `UmbracoForms` — affected >=0

## Details
### Impact
Within Umbraco Forms, configuring a malicious URL on the Webservice data source can result in Remote Code Execution. This affects all Umbraco Forms versions running on .NET Framework (up to and including version 8).

### Patches
The affected Umbraco Forms versions are all End-of-Life (EOL) and not supported anymore, hence no patches will be released. Upgrading to any of the currently supported versions (v13, v16 or v17) is recommended.

### Workarounds
If none of the configured Forms data sources uses the Webservice type, it can be safely excluded by adding the following code to the application. This will completely remove the option to select/use this data source within the Backoffice and thereby mitigate the vulnerability.

```c#
using Umbraco.Core.Composing;
using Umbraco.Forms.Core.Providers;
using Umbraco.Forms.Core.Providers.DatasourceTypes;

internal sealed class RemoveFormsWebserviceDataSourceTypeComposer : IUserComposer
{
    public void Compose(Composition composition)
        => composition.WithCollectionBuilder<DataSourceCollectionBuilder>().Exclude<Webservice>();
}
```

Any Webservice data source that is configured and still in use should be replaced with a custom implementation instead, before applying the above code. If this is not feasible, the vulnerability can be minimized by revoking the 'Manage Data Sources' from any non-administrator user and/or inheriting from the default `Umbraco.Forms.Core.Providers.DatasourceTypes.Webservice` class and overriding the `ValidateSettings()` method to ensure only trusted URLs can be used.

### References
When upgrading to a supported version, please take the Forms [version specific upgrade notes](https://docs.umbraco.com/umbraco-forms/13.latest/upgrading/version-specific) into account and check the [CMS upgrade documentation](https://docs.umbraco.com/umbraco-cms/13.latest/fundamentals/setup/upgrading). Content and schema can also be migrated straight to the latest version using [Deploy export/import with migrations](https://docs.umbraco.com/umbraco-deploy/13.latest/deployment-workflow/import-export).

Implementation details on data sources are not extensively documented, but they follow the general Forms [provider model](https://docs.umbraco.com/umbraco-forms/13.latest/developer/extending/adding-a-type) and inherit from `Umbraco.Forms.Core.FormDataSource`.

A special thanks to Piotr Bazydlo (@chudyPB) of watchTowr for finding and disclosing this vulnerability

## References
- https://github.com/umbraco/Umbraco.Forms.Issues/security/advisories/GHSA-vrgw-pc9c-qrrc
- https://nvd.nist.gov/vuln/detail/CVE-2025-68924
- https://github.com/advisories/GHSA-vrgw-pc9c-qrrc
- https://github.com/umbraco/Umbraco.Forms.Issues
- https://our.umbraco.com/packages/developer-tools/umbraco-forms
- https://www.nuget.org/packages/UmbracoForms

# [M] Microsoft Identity Web Exposes Client Secrets and Certificate Information in Service Logs

## Summary
Severity: Medium
Advisory: GHSA-rpq8-q44m-2rpg
CVE: CVE-2025-32016
CWE: CWE-532
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-04-09
Source: https://github.com/advisories/GHSA-rpq8-q44m-2rpg
Type: github-advisory

## Affected
- NuGet: `Microsoft.Identity.Web` — affected >=3.2.0 <3.8.2
- NuGet: `Microsoft.Identity.Abstractions` — affected >=7.1.0 <9.0.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

**Description:** This vulnerability affects confidential client applications, including daemons, web apps, and web APIs. Under specific circumstances, sensitive information such as client secrets or certificate details may be exposed in the service logs of these applications. Service logs are intended to be handled securely.

**Impact:** The vulnerability impacts service logs that meet the following criteria:

- **Logging Level:** Logs are generated at the information level.
- **Credential Descriptions:** containing:
    - Local file paths with passwords.
    - Base64 encoded values.
    - Client secret.
    
Additionally, logs of services using Base64 encoded certificates or certificate paths with password credential descriptions are also affected if the certificates are invalid or expired, regardless of the log level. Note that these credentials are not usable due to their invalid or expired status.

If your service logs are handled securely, you are not impacted. 

Otherwise, the following table shows when you can be impacted 
  | Log Level Information for Microsoft.Identity.Web | Invalid Certificate
-- | -- | --
One of the ClientCredentials credential description has a CredentialSource = Base64Encoded or (CredentialSource = Path) | Impacted | Impacted
One of the ClientCredentials credential description is a Client secret (CredentialSource = ClientSecret) | Impacted | Not impacted
Other credential descriptions | Not Impacted | Not Impacted

### Patches
_Has the problem been patched? What versions should users upgrade to?_
To mitigate this vulnerability, update to Microsoft.Identity.Web 3.8.2 or Microsoft.Identity.Abstractions 9.0.0.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
You can work around the issue in the following ways: 

- Ensure that service logs are handled securely and access to logs is restricted

- Don’t use `LogLevel = Information` for the Microsoft.Identity.Web namespace 

### Recommendation for production environment
Avoid using `ClientCredentials` with [`CredentialDescriptions`](https://learn.microsoft.com/en-us/dotnet/api/microsoft.identity.abstractions.credentialdescription.base64encodedvalue?view=msal-model-dotnet-latest) which `CredentialSource` is `ClientSecret`, or `Base64Encoded`, or `Path`. Rather use certificate from KeyVault or a certificate store, or Federation identity credential with Managed identity.

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/AzureAD/microsoft-identity-web/security/advisories/GHSA-rpq8-q44m-2rpg
- https://nvd.nist.gov/vuln/detail/CVE-2025-32016
- https://github.com/AzureAD/microsoft-identity-web

# [M] Test code in published microsoft-graph-core package exposes phpinfo()

## Summary
Severity: Medium
Advisory: GHSA-mhhp-c3cm-2r86
CVE: CVE-2023-49283
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-mhhp-c3cm-2r86
Type: github-advisory

## Affected
- Packagist: `microsoft/microsoft-graph-core` — affected >=0 <2.0.2

## Details
### Impact

The Microsoft Graph Core PHP SDK published packages which contained test code that enabled the use of the phpInfo() function from any application that could access and execute the file at vendor/microsoft/microsoft-graph-core/tests/GetPhpInfo.php.  The phpInfo function exposes system information. 

The vulnerability affects the GetPhpInfo.php script of the PHP SDK which contains a call to the phpinfo() function.  

This vulnerability requires a misconfiguration of the server to be present so it can be exploited. For example, making the PHP application’s /vendor directory web accessible.  

The combination of the vulnerability and the server misconfiguration would allow an attacker to craft an HTTP request that executes the phpinfo() method. The attacker would then be able to get access to system information like configuration, modules, and environment variables and later on use the compromised secrets to access additional data.

### Patches

This problem has been patched in version 2.0.2.

### Workarounds

If an immediate deployment with the updated vendor package is not available, you can perform the following temporary workarounds:
- delete the vendor/microsoft/microsoft-graph-core/tests/GetPhpInfo.php file
- remove access to the /vendor directory will remove this vulnerability
- disable the phpinfo function

### References
For more information about the vulnerability and the patch, users can refer to the following sources: 

- https://nvd.nist.gov/vuln/detail/CVE-2023-49103
- https://github.com/microsoftgraph/msgraph-beta-sdk-php/compare/2.0.0...2.0.1 
- https://github.com/microsoftgraph/msgraph-sdk-php-core/compare/2.0.1...2.0.2 
- https://github.com/microsoftgraph/msgraph-sdk-php/compare/1.109.0...1.109.1 
- https://owncloud.com/security-advisories/disclosure-of-sensitive-credentials-and-configuration-in-containerized-deployments/

## References
- https://github.com/microsoftgraph/msgraph-sdk-php-core/security/advisories/GHSA-mhhp-c3cm-2r86
- https://nvd.nist.gov/vuln/detail/CVE-2023-49103
- https://nvd.nist.gov/vuln/detail/CVE-2023-49283
- https://github.com/FriendsOfPHP/security-advisories/blob/master/microsoft/microsoft-graph-core/CVE-2023-49283.yaml
- https://github.com/microsoftgraph/msgraph-beta-sdk-php/compare/2.0.0...2.0.1
- https://github.com/microsoftgraph/msgraph-sdk-php-core
- https://github.com/microsoftgraph/msgraph-sdk-php-core/compare/2.0.1...2.0.2
- https://github.com/microsoftgraph/msgraph-sdk-php/compare/1.109.0...1.109.1
- https://owncloud.com/security-advisories/disclosure-of-sensitive-credentials-and-configuration-in-containerized-deployments

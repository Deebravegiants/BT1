# [M] ZendFramework Potential Cross-site Scripting in Development Environment Error View Script

## Summary
Severity: Medium
Advisory: GHSA-g52p-86j5-xr8q
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-g52p-86j5-xr8q
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.0.0 <1.11.4

## Details
The default error handling view script generated using `Zend_Tool` failed to escape request parameters when run in the "development" configuration environment, providing a potential XSS attack vector.

`Zend_Tool_Project_Context_Zf_ViewScriptFile` was patched such that the view script template now calls the `escape()` method on dumped request variables.

Zend Framework 1.11.4 includes a patch that adds escaping to the generated error/error.phtml view script, ensuring that request variables are escaped appropriately for the browser.
Do note, however, that this will not update any previously generated code. You will still need to follow the next advice for previously generated error view scripts.

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2011-01.yaml
- https://github.com/zendframework/zf1
- https://web.archive.org/web/20210120123405/https://framework.zend.com/security/advisory/ZF2011-01

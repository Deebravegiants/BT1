# [H] TYPO3 is vulnerable to Cross-Site Scripting via frontend rendering

## Summary
Severity: High
Advisory: GHSA-r4f8-f93x-5qh3
CVE: CVE-2023-24814
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2023-02-08
Source: https://github.com/advisories/GHSA-r4f8-f93x-5qh3
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.2.0
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.23
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.36
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.40
- Packagist: `typo3/cms-core` — affected >=8.7.0 <8.7.51
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.35
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.23
- Packagist: `typo3/cms` — affected >=12.0.0 <12.2.0

## Details
> ### CVSS: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L/E:F/RL:O/RC:C` (8.2)

### Problem
TYPO3 core component `GeneralUtility::getIndpEnv()` uses the unfiltered server environment variable `PATH_INFO`, which allows attackers to inject malicious content.

In combination with the TypoScript setting [`config.absRefPrefix=auto`](https://github.com/TYPO3/typo3/blob/v11.5.22/typo3/sysext/frontend/Classes/Controller/TypoScriptFrontendController.php#L2547-L2549), attackers can inject malicious HTML code into pages that have not yet been rendered and cached. As a result, injected values would be cached and delivered to other website visitors (persisted cross-site scripting).

Individual code which relies on the resolved value of [`GeneralUtility::getIndpEnv('SCRIPT_NAME')`](https://github.com/TYPO3/typo3/blob/v11.5.22/typo3/sysext/core/Classes/Utility/GeneralUtility.php#L2481-L2484) and corresponding usages (as shown below) are vulnerable as well.

- `GeneralUtility::getIndpEnv('PATH_INFO') `
- `GeneralUtility::getIndpEnv('SCRIPT_NAME') `
- `GeneralUtility::getIndpEnv('TYPO3_REQUEST_DIR')`
- `GeneralUtility::getIndpEnv('TYPO3_REQUEST_SCRIPT')`
- `GeneralUtility::getIndpEnv('TYPO3_SITE_PATH')`
- `GeneralUtility::getIndpEnv('TYPO3_SITE_SCRIPT')`
- `GeneralUtility::getIndpEnv('TYPO3_SITE_URL')`

Installations of TYPO3 versions 8.7 and 9.x are probably only affected when server environment variable [`TYPO3_PATH_ROOT`](https://docs.typo3.org/m/typo3/reference-coreapi/9.5/en-us/ApiOverview/Environment/Index.html#configuring-environment-paths) is defined - which is the case if they were installed via Composer.

Additional investigations confirmed that Apache and Microsoft IIS web servers using PHP-CGI (FPM, FCGI/FastCGI, or similar) are affected. There might be the risk that nginx is vulnerable as well. It was not possible to exploit Apache/mod_php scenarios.

### Solution
The usage of server environment variable `PATH_INFO` has been removed from corresponding processings in `GeneralUtility::getIndpEnv()`. Besides that, the public property `TypoScriptFrontendController::$absRefPrefix` is encoded for both being used as a URI component and for being used as a prefix in an HTML context. This mitigates the cross-site scripting vulnerability.

Update to TYPO3 versions 8.7.51 ELTS, 9.5.40 ELTS, 10.4.36 LTS, 11.5.23 LTS and 12.2.0 that fix the problem described above.

> ℹ️ **Strong security defaults - Manual actions required**
> Any web server using PHP-CGI (FPM, FCGI/FastCGI, or similar) needs to ensure that the PHP setting [**`cgi.fix_pathinfo=1`**](https://www.php.net/manual/en/ini.core.php#ini.cgi.fix-pathinfo) is used, which is the default PHP setting. In case this setting is not enabled, an exception is thrown to avoid continuing with invalid path information.

For websites that cannot be patched timely the TypoScript setting [`config.absRefPrefix`](https://docs.typo3.org/m/typo3/reference-typoscript/main/en-us/Setup/Config/Index.html#absrefprefix) at least should be set to a static path value, instead of using `auto` - e.g. `config.absRefPrefix=/` - this **does not fix all aspects of the vulnerability**, and is just considered to be an intermediate mitigation to the most prominent manifestation.

### References
* [TYPO3-CORE-SA-2023-001](https://typo3.org/security/advisory/typo3-core-sa-2023-001)
* [TYPO3-CORE-PSA-2023-001](https://typo3.org/security/advisory/typo3-psa-2023-001) *pre-announcement*

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-r4f8-f93x-5qh3
- https://nvd.nist.gov/vuln/detail/CVE-2023-24814
- https://github.com/TYPO3/typo3/commit/0005a6fd86ab97eff8bf2e3a5828bf0e7cb6263a
- https://docs.typo3.org/m/typo3/reference-typoscript/main/en-us/Setup/Config/Index.html#absrefprefix
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2023-24814.yaml
- https://github.com/TYPO3/typo3
- https://github.com/TYPO3/typo3/blob/v11.5.22/typo3/sysext/core/Classes/Utility/GeneralUtility.php#L2481-L2484
- https://github.com/TYPO3/typo3/blob/v11.5.22/typo3/sysext/frontend/Classes/Controller/TypoScriptFrontendController.php#L2547-L2549
- https://typo3.org/security/advisory/typo3-core-sa-2023-001
- https://typo3.org/security/advisory/typo3-psa-2023-001

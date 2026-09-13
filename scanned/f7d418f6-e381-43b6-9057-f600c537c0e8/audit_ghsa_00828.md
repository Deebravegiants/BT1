# [M] Reliance on Cookies without validation in OctoberCMS

## Summary
Severity: Medium
Advisory: GHSA-55mm-5399-7r63
CVE: CVE-2020-15128
CWE: CWE-327, CWE-565
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-08-05
Source: https://github.com/advisories/GHSA-55mm-5399-7r63
Type: github-advisory

## Affected
- Packagist: `october/rain` — affected >=1.0.319 <1.0.468

## Details
### Impact
Previously encrypted cookie values were not tied to the name of the cookie the value belonged to. This meant that certain classes of attacks that took advantage of other theoretical vulnerabilities in user facing code (nothing exploitable in the core project itself) had a higher chance of succeeding. 

Specifically, if your usage exposed a way for users to provide unfiltered user input and have it returned to them as an encrypted cookie (ex. storing a user provided search query in a cookie) they could then use the generated cookie in place of other more tightly controlled cookies; or if your usage exposed the plaintext version of an encrypted cookie at any point to the user they could theoretically provide encrypted content from your application back to it as an encrypted cookie and force the framework to decrypt it for them. 

### Patches
Issue has been patched in Build 468 (v1.0.468).

>**NOTE**: If you are using the cookie session driver, all of your session data will be invalidated. All other session drivers should smoothly upgrade to the changes (although the backend authentication persist cookie will also be invalidated requiring users to login again once their current session expires).

### Workarounds
Apply https://github.com/octobercms/library/commit/28310d4fb336a1741b39498f4474497644a6875c to your installation manually if unable to upgrade to Build 468.

### References
- https://blog.laravel.com/laravel-cookie-security-releases
- https://github.com/laravel/framework/compare/4c7d118181d6c7f1f883643702df807ced016c5e...a731824421f9ebc586728ea9c7cff231a249aaa9

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat Assessment
Assessed as Low given that it is not directly exploitable within the core but requires other security vulnerabilities within the application to have an effect and the severity of its effect depends entirely on the severity of those other holes in the application's defences.

### Acknowledgements

Thanks to [Takashi Terada of Mitsui Bussan Secure Directions, Inc.](https://www.linkedin.com/in/takeshi-terada-b570a6100/) for finding the original issue in Laravel and @taylorotwell for sharing the report with the October CMS team.

## References
- https://github.com/octobercms/october/security/advisories/GHSA-55mm-5399-7r63
- https://nvd.nist.gov/vuln/detail/CVE-2020-15128
- https://github.com/octobercms/library/pull/508
- https://github.com/octobercms/library/commit/28310d4fb336a1741b39498f4474497644a6875c

# [H] October CMS auth bypass and account takeover

## Summary
Severity: High
Advisory: GHSA-h76r-vgf3-j6w5
CVE: CVE-2021-29487
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-h76r-vgf3-j6w5
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=0 <1.0.472
- Packagist: `october/system` — affected >=1.1.1 <1.1.5

## Details
### Impact

An attacker can exploit this vulnerability to bypass authentication using a specially crafted persist cookie.

- To exploit this vulnerability, an attacker must obtain a Laravel’s secret key for cookie encryption and signing.
- Due to the logic of how this mechanism works, a targeted user account must be logged in while
the attacker is exploiting the vulnerability.
- Authorization via persist cookie not shown in access logs.

### Patches

- Issue has been patched in Build 472 and v1.1.5
- [Shortened patch instructions](https://github.com/daftspunk/CVE-2021-32648)

### Workarounds

Apply https://github.com/octobercms/library/commit/016a297b1bec55d2e53bc889458ed2cb5c3e9374 and https://github.com/octobercms/library/commit/5bd1a28140b825baebe6becd4f7562299d3de3b9 to your installation manually if you are unable to upgrade.

[**Update 2022-01-20**] [Shortened patch instructions](https://github.com/daftspunk/CVE-2021-32648) can be found here.

### Recommendations

We recommend the following steps to make sure your server stays secure:

- Keep server OS and system software up to date.
- Keep October CMS software up to date.
- Use a multi-factor authentication plugin.
- Change the [default backend URL](https://github.com/octobercms/october/blob/1.1/config/cms.php#L39) or block public access to the backend area.
- Include the [Roave/SecurityAdvisories](https://github.com/Roave/SecurityAdvisories) Composer package to ensure that your application doesn't have installed dependencies with known security vulnerabilities.

### References

Bugs found as part of Solar Security CMS Research. Credits to:
• Andrey Basarygin
• Andrey Guzei
• Mikhail Khramenkov
• Alexander Sidukov
• Maxim Teplykh

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-h76r-vgf3-j6w5
- https://nvd.nist.gov/vuln/detail/CVE-2021-29487
- https://github.com/octobercms/library/commit/016a297b1bec55d2e53bc889458ed2cb5c3e9374
- https://github.com/octobercms/library/commit/5bd1a28140b825baebe6becd4f7562299d3de3b9
- https://github.com/octobercms/october

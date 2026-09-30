# [M] Kirby CMS vulnerable to user enumeration in the code-based login and password reset forms

## Summary
Severity: Medium
Advisory: GHSA-43qq-qw4x-28f8
CVE: CVE-2022-39314
CWE: CWE-204, CWE-307
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-43qq-qw4x-28f8
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=3.5.0 <3.5.8.2
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.2
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.1
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.1

## Details
### TL;DR

This vulnerability only affects you if you are using the `code` or `password-reset` auth method with the `auth.methods` option. It can only be successfully exploited under server configuration conditions outside of the attacker's control.

----

### Introduction

User enumeration is a type of vulnerability that allows attackers to confirm which users are registered in a Kirby installation. This information can be abused for social engineering attacks against users of the site or to find out the organizational structure of the company.

User enumeration attacks are performed by entering an existing and a non-existing user into the email address field of the login form. If the system returns a different response or behaves differently depending on whether the user exists, the attacker can enter unknown email addresses and use the different behavior as a clue for the (non-)existing user.

### Impact

Under normal circumstances, entering an invalid email address results in a "fake" login code form that looks exactly like the one of an existing user (unless debugging is enabled). However, the code that handles the creation of a code challenge (for code-based login or password reset) didn't catch errors that occurred while the challenge request was processed:

- If the challenge itself runs into an error (e.g. if the email could not be sent), attackers could tell existing users (where the challenge code is called) from non-existing users (where the challenge code is not called and therefore does not output an error).
- If you are using the `user.login:failed` hook and any exception is thrown within the hook, attackers could see that the user does not exist.

As long as no error occurs during challenge creation and during the processing of the `user.login:failed` hook, your Kirby sites are *not* affected by this vulnerability.

### Patches

The problems have been patched in [Kirby 3.5.8.2](https://github.com/getkirby/kirby/releases/tag/3.5.8.2), [Kirby 3.6.6.2](https://github.com/getkirby/kirby/releases/tag/3.6.6.2), [Kirby 3.7.5.1](https://github.com/getkirby/kirby/releases/tag/3.7.5.1) and [Kirby 3.8.1](https://github.com/getkirby/kirby/releases/tag/3.8.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

All of the mentioned releases contain two patches for this vulnerability:

- All errors that occur during the creation of an auth challenge (code-based login or password reset) are swallowed by the backend and only displayed to the user if debugging is enabled.
- We added a new `auth.debug` option that can be enabled separately from the `debug` option. If disabled, auth errors are only printed to the PHP error log. This ensures that security-critical errors are only displayed if they are really necessary for debugging.

### Workarounds

We recommend to update to one of the patch releases. If you cannot update immediately, you can work around the issue by setting the `auth.methods` option to `password`, which disables the code-based login and password reset forms.

However please note that your site will still be vulnerable against [another user enumeration issue](https://github.com/getkirby/kirby/security/advisories/GHSA-c27j-76xg-6x4f) that was also fixed in the same patch releases.

### Credits

Thanks to [Florian Merz](mailto:florian@hatchery.io) (@florianmrz) of [hatchery.io](https://www.hatchery.io/) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-43qq-qw4x-28f8
- https://nvd.nist.gov/vuln/detail/CVE-2022-39314
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.2
- https://github.com/getkirby/kirby/releases/tag/3.6.6.2
- https://github.com/getkirby/kirby/releases/tag/3.7.5.1
- https://github.com/getkirby/kirby/releases/tag/3.8.1

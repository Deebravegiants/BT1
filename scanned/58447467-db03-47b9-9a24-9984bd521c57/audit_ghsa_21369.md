# [M] Kirby CMS vulnerable to user enumeration in the brute force protection

## Summary
Severity: Medium
Advisory: GHSA-c27j-76xg-6x4f
CVE: CVE-2022-39315
CWE: CWE-204, CWE-209, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-18
Source: https://github.com/advisories/GHSA-c27j-76xg-6x4f
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.2
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.2
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.1
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.1

## Details
### TL;DR

This vulnerability affects all Kirby sites with user accounts (unless Kirby's API and Panel are disabled in the config). It can only be exploited for targeted attacks because the attack does not scale to brute force.

----

### Introduction

User enumeration is a type of vulnerability that allows attackers to confirm which users are registered in a Kirby installation. This information can be abused for social engineering attacks against users of the site or to find out the organizational structure of the company.

User enumeration attacks are performed by entering an existing and a non-existing user into the email address field of the login form. If the system returns a different response or behaves differently depending on whether the user exists, the attacker can enter unknown email addresses and use the different behavior as a clue for the (non-)existing user.

### Impact

Kirby comes with a built-in brute force protection. By default, it will prevent further login attempts after 10 failed logins from a single IP address or of a single existing user. After every failed login attempt, Kirby inserts a random delay between one millisecond and two seconds to make automated attacks harder and to avoid leaking whether the user exists. Unfortunately, this random delay was not inserted after the brute force limit was reached.

Because Kirby only tracks failed login attempts per email address for existing users but always tracks failed login attempts per IP address, this behavior could be abused by attackers for user enumeration. For this to work, an attacker would need to create login requests beyond the trials limit (which is 10 by default) from two or more IP addresses. After the trials limit was reached, the login form immediately blocked further requests for existing users, but not for invalid users.

This exploit does not scale to brute force attacks because of the delay during the first 10 requests per user, the faint difference between the responses for valid and invalid users and the fact that code-based logins would send an email for every login attempt, which makes the attack easy to spot. The vulnerability is therefore only relevant for targeted attacks.

### Patches

The problem has been patched in [Kirby 3.5.8.2](https://github.com/getkirby/kirby/releases/tag/3.5.8.2), [Kirby 3.6.6.2](https://github.com/getkirby/kirby/releases/tag/3.6.6.2), [Kirby 3.7.5.1](https://github.com/getkirby/kirby/releases/tag/3.7.5.1) and [Kirby 3.8.1](https://github.com/getkirby/kirby/releases/tag/3.8.1). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have rewritten the affected code so that the delay is also inserted after the brute force limit is reached.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-c27j-76xg-6x4f
- https://nvd.nist.gov/vuln/detail/CVE-2022-39315
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.2
- https://github.com/getkirby/kirby/releases/tag/3.6.6.2
- https://github.com/getkirby/kirby/releases/tag/3.7.5.1
- https://github.com/getkirby/kirby/releases/tag/3.8.1

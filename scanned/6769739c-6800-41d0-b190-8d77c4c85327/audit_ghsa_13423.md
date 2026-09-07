# [M] Denial of service from unlimited password lengths

## Summary
Severity: Medium
Advisory: GHSA-3v6j-v3qc-cxff
CVE: CVE-2023-38492
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-3v6j-v3qc-cxff
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.8.3
- Packagist: `getkirby/cms` — affected >=3.6.0 <3.6.6.3
- Packagist: `getkirby/cms` — affected >=3.7.0 <3.7.5.2
- Packagist: `getkirby/cms` — affected >=3.8.0 <3.8.4.1
- Packagist: `getkirby/cms` — affected >=3.9.0 <3.9.6

## Details
### TL;DR

This vulnerability affects all Kirby sites with user accounts (unless Kirby's API and Panel are disabled in the config). The real-world impact of this vulnerability is limited, however we still recommend to update to one of the patch releases because they also fix more severe vulnerabilities.

----

### Introduction

Denial of service (DoS) is a type of attack in which an attacker floods a service with the intention to limit performance or availability for legitimate users of the service.

In the variation described in this advisory (a so called application layer denial of service attack), it is performed by causing a computationally expensive task to be run on the server. This may then cause a performance bottleneck.

### Impact

Kirby's authentication endpoint did not limit the password length. This allowed attackers to provide a password with a length up to the server's maximum request body length. Validating that password against the user's actual password requires hashing the provided password, which requires more CPU and memory resources (and therefore processing time) the longer the provided password gets. This could be abused by an attacker to cause the website to become unresponsive or unavailable.

Because Kirby comes with a built-in brute force protection, the impact of this vulnerability is limited to 10 failed logins from each IP address and 10 failed logins for each existing user per hour.

### Patches

The problem has been patched in [Kirby 3.5.8.3](https://github.com/getkirby/kirby/releases/tag/3.5.8.3), [Kirby 3.6.6.3](https://github.com/getkirby/kirby/releases/tag/3.6.6.3), [Kirby 3.7.5.2](https://github.com/getkirby/kirby/releases/tag/3.7.5.2), [Kirby 3.8.4.1](https://github.com/getkirby/kirby/releases/tag/3.8.4.1) and [Kirby 3.9.6](https://github.com/getkirby/kirby/releases/tag/3.9.6). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we have added password length limits in the affected code so that passwords longer than 1000 bytes are immediately blocked, both when setting a password and when logging in.

### Credits

Thanks to Shankar Acharya (@5hank4r) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-3v6j-v3qc-cxff
- https://nvd.nist.gov/vuln/detail/CVE-2023-38492
- https://github.com/getkirby/kirby/commit/0e10ce3b0c2b88656564b8ff518ddc99136ac43e
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/3.5.8.3
- https://github.com/getkirby/kirby/releases/tag/3.6.6.3
- https://github.com/getkirby/kirby/releases/tag/3.7.5.2
- https://github.com/getkirby/kirby/releases/tag/3.8.4.1
- https://github.com/getkirby/kirby/releases/tag/3.9.6

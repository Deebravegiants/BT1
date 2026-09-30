# [C] Pterodactyl Panel Allows Unauthenticated Arbitrary Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-24wv-6c99-f843
CVE: CVE-2025-49132
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-19
Source: https://github.com/advisories/GHSA-24wv-6c99-f843
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.11.11

## Details
## Impact

Using the `/locales/locale.json` with the `locale` and `namespace` query parameters, a malicious actor is able to execute arbitrary code, without being authenticated.

With the ability to execute arbitrary code, this vulnerability can be exploited in an infinite number of ways.  It could be used to gain access to the Panel's server, read credentials from the Panel's config (`.env` or otherwise), extract sensitive information from the database (such as user details [username, email, first and last name, hashed password, ip addresses, etc]), access files of servers managed by the panel, etc.

## Patches

This vulnerability was patched by https://github.com/pterodactyl/panel/commit/24c82b0e335fb5d7a844226b08abf9f176e592f0 and was released under the [`v1.11.11`](https://github.com/pterodactyl/panel/releases/tag/v1.11.11) tag without any other code modifications compared to `v1.11.10`.

For those who need to patch their installations in-place or apply it on top of other code modifications, a patch file can be retrieved from <https://github.com/pterodactyl/panel/commit/24c82b0e335fb5d7a844226b08abf9f176e592f0.patch> and applied using `git apply`.

## Workarounds

Other than patching the software, there is no workaround in this software.  Disabling the `/locales/locale.json` endpoint at the webserver level is possible, but would break the localization feature wherever it is used.

The only other workaround relies on an external Web Application Firewall (WAF), such as Cloudflare's WAF with their default ruleset (requires Pro plan or above, Free doesn't have the proper ruleset) to mitigate this attack.

Updating to [`v1.11.11`](https://github.com/pterodactyl/panel/releases/tag/v1.11.11) or manually patching the software are the only recommended ways to completely mitigate this vulnerability.

## User Notice

Shortly after the [`v1.11.11`](https://github.com/pterodactyl/panel/releases/tag/v1.11.11)release and it's announcement, security researchers and malicious actors have been attempting to exploit this vulnerability.  While there hasn't been any official confirmations of breaches or successful exploits of the vulnerability in the wild, it is only a matter of time for those who remain on unpatched versions without any workarounds in place.

The scope of this vulnerability cannot be fully described, anything is possible.  It is of utmost importance that anyone running a vulnerable version of this software, patch it or update to the latest available version **immediately**.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-24wv-6c99-f843
- https://nvd.nist.gov/vuln/detail/CVE-2025-49132
- https://github.com/pterodactyl/panel/commit/24c82b0e335fb5d7a844226b08abf9f176e592f0
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.11.11

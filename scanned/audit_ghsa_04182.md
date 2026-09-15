# [C] Kirby: External Initialization of the Panel on reverse proxy setups with the `Forwarded` header

## Summary
Severity: Critical
Advisory: GHSA-whxw-24jc-cwmv
CVE: CVE-2026-54003
CWE: CWE-454
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-whxw-24jc-cwmv
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <4.9.4
- Packagist: `getkirby/cms` — affected >=5.0.0-alpha.1 <5.4.4

## Details
### TL;DR

This vulnerability affects Kirby sites that have no configured user accounts and are running on publicly accessible servers behind a reverse proxy that sets the `Forwarded: for=...`, `X-Client-IP`, or `X-Real-IP` request header.

It was possible to install the Panel (= create the first admin user) in these setups even from remote IP addresses.

**This vulnerability is of critical severity for affected sites.**

Your site is *not* affected if any of the following apply: 

- An admin account has already been configured
- The Panel and API are disabled
- The site is not running behind a reverse proxy
- The reverse proxy sets the `X-Forwarded-For` or `Client-IP` header instead of the affected ones.

----

### Introduction

External Initialization is a type of vulnerability that allows attackers to initialize a system or configuration value without authentication.

This can give untrusted actors access to the system or let them control its behavior.

### Affected components

The Kirby Panel and REST API are authenticated by local user accounts. If a Kirby installation does not yet have any users, it first needs to be installed. During the installation process, an initial admin user account is created.

To protect against external initialization attacks that would allow untrusted actors to create an admin user for the Kirby installation, Kirby already checked whether the current request came from a local IP address. This allows installing the Panel in local development setups. Installation on remote servers was only supposed to be possible when the `panel.install` configuration option was enabled.

The `isLocal` check takes all relevant request headers into account and treats a request as non-local as soon as any checked request header contains an external IP address.

### Impact

In affected releases, the `isLocal` check for the installation logic did not properly take the `Forwarded: for=...` header into account. This header is set by modern reverse proxy servers. It also did not take into account the `X-Client-IP` or `X-Real-IP` headers, which are set by some custom reverse proxy setups.

This caused Kirby to falsely assume that an installation request was local and allowed creating an admin account even though the reverse proxy forwarded the request from an external IP address.

Reverse proxies setting the `X-Forwarded-For` or `Client-IP` headers were *not* affected. These headers were already properly checked for external IP addresses.

### Patches

The problem has been patched in [Kirby 4.9.4](https://github.com/getkirby/kirby/releases/tag/4.9.4) and [Kirby 5.4.4](https://github.com/getkirby/kirby/releases/tag/5.4.4). Please update to one of these or a [later version](https://github.com/getkirby/kirby/releases) to fix the vulnerability.

In all of the mentioned releases, we fixed the `isLocal` check to also properly take `Forwarded: for=...`, `X-Client-IP` and `X-Real-IP` request headers into account.

### Workarounds

Sites on older Kirby versions (Kirby 3 starting at 3.7.0) can be protected with one of the following workarounds:

- Perform the Panel installation yourself by creating an initial admin account. As soon as one or more accounts are present, the vulnerable installation code is no longer active.
- If you don't need the Panel, disable the REST API with the `'api' => false` option in `config.php`.

### Credits

Thanks to Peter Levashov (@petersevera) for responsibly reporting the identified issue.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-whxw-24jc-cwmv
- https://github.com/getkirby/kirby
- https://github.com/getkirby/kirby/releases/tag/4.9.4
- https://github.com/getkirby/kirby/releases/tag/5.4.4

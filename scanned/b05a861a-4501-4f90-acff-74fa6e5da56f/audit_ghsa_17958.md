# [M] WP Crontrol Authenticated (Administrator+) plugin vulnerable to Blind Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-35c5-67fm-cpcp
CVE: CVE-2025-8678
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:L/VA:L/SC:N/SI:L/SA:L (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-35c5-67fm-cpcp
Type: github-advisory

## Affected
- Packagist: `johnbillion/wp-crontrol` — affected >=1.17.0 <1.19.2

## Details
### Impact

The WP Crontrol plugin for WordPress is vulnerable to Blind Server-Side Request Forgery in versions 1.17.0 to 1.19.1 via the `wp_remote_request()` function. This makes it possible for authenticated attackers, with Administrator-level access and above, to make web requests to arbitrary locations originating from the web application and can be used to query and modify information from internal services.

It is not possible for a user without Administrator level access to exploit this weakness. It is not possible for an Administrator performing an attack to see the HTTP response to the request to their chosen URL, nor is it possible for them to time the response.

### Patches

WP Crontrol version 1.19.2 makes the following changes to harden the URL cron event feature:

* URLs are now validated for safety with the `wp_http_validate_url()` function upon saving. The user is informed if they save a cron event containing a URL that is not considered safe, and the HTTP request will not trigger when the event runs.
* HTTP requests are now performed via the `wp_safe_remote_request()` function in place of `wp_remote_request()`. This prevents an SSRF being performed.

### Workarounds

Update the WP Crontrol plugin for WordPress to version 1.19.2 or later. If you are not able to update immediately, remove any Administrator level users who are not fully trusted.

### FAQ

#### Is my site at risk?

Your site is only at risk if an untrustworthy Administrator on your site decides to exploit this weakness in order to blindly send HTTP requests, either to external URLs or to internal services running on your server. These requests can only be performed asynchronously, which means the HTTP response cannot be seen nor timed, which significantly restricts the practical methods of exploiting this weakness.

Separately, it is not possible for an attacker with database level access on your server to tamper with a URL cron event and perform an SSRF due to [the anti-tampering measures built in to WP Crontrol](https://wp-crontrol.com/docs/url-cron-events/).

### Thanks

This issue was identified by [Jonas Benjamin Friedli](https://github.com/jFriedli) and reported to the Wordfence Intelligence Bug Bounty Program.

[Security bugs should be reported through the official WP Crontrol Vulnerability Disclosure Program on Patchstack](https://patchstack.com/database/vdp/wp-crontrol). The Patchstack team helps validate, triage, and handle any security vulnerabilities.

## References
- https://github.com/johnbillion/wp-crontrol/security/advisories/GHSA-35c5-67fm-cpcp
- https://github.com/johnbillion/wp-crontrol/commit/b085bd306588d7a9baed82de37f9d1818deafc44
- https://github.com/johnbillion/wp-crontrol
- https://github.com/johnbillion/wp-crontrol/releases/tag/1.19.2

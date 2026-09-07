# [M] Silverstripe Hostname, IP and Protocol Spoofing through HTTP Headers

## Summary
Severity: Medium
Advisory: GHSA-87pf-7x99-5xc4
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-87pf-7x99-5xc4
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <3.1.17
- Packagist: `silverstripe/framework` — affected >=3.2.0 <3.2.2
- Packagist: `silverstripe/framework` — affected >=3.3.0-beta1 <3.3.0

## Details
In it's default configuration, SilverStripe trusts all originating IPs to include HTTP headers for Hostname, IP and Protocol. This enables reverse proxies to forward requests while still retaining the original request information. Trusted IPs can be limited via the SS_TRUSTED_PROXY_IPS constant. Even with this restriction in place, SilverStripe trusts a variety of HTTP headers due to different proxy notations (e.g. X-Forwarded-For vs. Client-IP). Unless a proxy explicitly unsets invalid HTTP headers from connecting clients, this can lead to spoofing requests being passed through trusted proxies.

The impact of spoofed headers can include Director::forceSSL() not being enforced, SS_HTTPRequest->getIP() returning a wrong IP (disabling any IP restrictions), and spoofed hostnames circumventing any hostname-specific restrictions enforced in SilverStripe Controllers.

Regardless on running a reverse proxy in your hosting infrastructure, please follow the instructions on Secure Coding: Request hostname forgery in order to opt-in to these protections. If your website is not behind a reverse proxy, you might already be protected if using Apache with mod_env enabled, and you have the following line in your .htaccess file: SetEnv BlockUntrustedIPs true.

## References
- https://github.com/silverstripe/silverstripe-framework/commit/37059eb6b3546f304e9c031abca0f096ddb175c6
- https://github.com/silverstripe/silverstripe-framework/commit/893e49703de4aa1855b5364919cbb0826f754fbf
- https://github.com/silverstripe/silverstripe-framework/commit/faa94d51d570788dcebc2f2ef6e9de4d179ce1e4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2016-003-1.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2016-003

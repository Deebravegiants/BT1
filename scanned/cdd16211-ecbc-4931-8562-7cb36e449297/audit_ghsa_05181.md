# [M] Symfony: IpUtils::PRIVATE_SUBNETS Omits IPv6 Transition Forms (6to4, NAT64, Teredo, IPv4-compatible): SSRF Bypass in NoPrivateNetworkHttpClient

## Summary
Severity: Medium
Advisory: GHSA-38cx-cq6f-5755
CVE: CVE-2026-48736
CWE: CWE-184, CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-38cx-cq6f-5755
Type: github-advisory

## Affected
- Packagist: `symfony/http-client` — affected >=5.4.0 <5.4.53
- Packagist: `symfony/http-foundation` — affected >=6.4.0 <6.4.41
- Packagist: `symfony/http-foundation` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/http-foundation` — affected >=8.0.0 <8.0.13
- Packagist: `symfony/symfony` — affected >=5.4.0 <5.4.53
- Packagist: `symfony/symfony` — affected >=6.4.0 <6.4.41
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.13

## Details
### Description

`Symfony\Component\HttpClient\NoPrivateNetworkHttpClient` is documented as a decorator that blocks requests to private networks by default. The list of blocked subnets (`Symfony\Component\HttpFoundation\IpUtils::PRIVATE_SUBNETS` on 6.4+, a private constant in `NoPrivateNetworkHttpClient` on 5.4) enumerates RFC1918, loopback, link-local and IPv4-mapped IPv6 (`::ffff:0:0/96`) prefixes, but omits the remaining IPv6 transition forms that can embed a private IPv4 destination: 6to4 (`2002::/16`, RFC 3056), Teredo (`2001::/32`, RFC 4380), NAT64 (`64:ff9b::/96`, RFC 6052 and `64:ff9b:1::/48`, RFC 8215) and IPv4-compatible IPv6 (`::/96`, RFC 4291 §2.5.5.1).

`IpUtils::checkIp6()` is a pure bitwise CIDR comparison against the constants list and never extracts the embedded IPv4, so an attacker who can supply a URL writes the loopback / RFC1918 IPv4 target as e.g. `http://[2002:7f00:1::]/` (6to4 → 127.0.0.1), `http://[64:ff9b::7f00:1]/` (NAT64 → 127.0.0.1), `http://[::7f00:1]/` (IPv4-compatible → 127.0.0.1) or `http://[2001::1]/` (Teredo). `IpUtils::isPrivateIp()` returns `false` and `NoPrivateNetworkHttpClient` dispatches the request.

Real-world reachability of the embedded IPv4 depends on the deploy's IPv6 routing (6to4 tunnel interface, upstream NAT64 gateway, kernel handling of IPv4-compatible addresses), but the security boundary the decorator promises — the dispatch decision — is crossed regardless of whether the packet ultimately lands on the embedded IPv4.

### Resolution

The private-subnet list now includes `::/96`, `2002::/16`, `2001::/32`, `64:ff9b::/96` and `64:ff9b:1::/48`. Blanket blocking of these prefixes matches the policy applied by Chromium and Mozilla's Private Network Access; server-side HTTPS APIs are not legitimately published on these prefixes.

The patches for this issue are available [here](https://github.com/symfony/symfony/commit/82765368cf74177c36613575182f168a2eb765b2) for branch 5.4 and [here](https://github.com/symfony/symfony/commit/85b831555be8ea1f43bf01078afe87bc4c92f65e) for branch 6.4 (and forward-ported to 7.4, 8.0 and 8.1).

### Credits

Symfony would like to thank tonghuaroot for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-38cx-cq6f-5755
- https://github.com/symfony/symfony/commit/82765368cf74177c36613575182f168a2eb765b2
- https://github.com/symfony/symfony/commit/85b831555be8ea1f43bf01078afe87bc4c92f65e
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-client/CVE-2026-48736.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/http-foundation/CVE-2026-48736.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48736.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48736

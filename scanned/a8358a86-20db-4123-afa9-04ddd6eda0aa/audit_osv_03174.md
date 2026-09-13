# [M] ALPINE-CVE-2024-9681

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-9681
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2024-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-9681
Type: osv

## Affected
- Alpine:v3.18: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.19: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.20: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.21: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.22: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.23: `curl` — affected >=7.74.0 <8.11.0-r0
- Alpine:v3.24: `curl` — affected >=7.74.0 <8.11.0-r0

## Details
When curl is asked to use HSTS, the expiry time for a subdomain might
overwrite a parent domain's cache entry, making it end sooner or later than
otherwise intended.

This affects curl using applications that enable HSTS and use URLs with the
insecure `HTTP://` scheme and perform transfers with hosts like
`x.example.com` as well as `example.com` where the first host is a subdomain
of the second host.

(The HSTS cache either needs to have been populated manually or there needs to
have been previous HTTPS accesses done as the cache needs to have entries for
the domains involved to trigger this problem.)

When `x.example.com` responds with `Strict-Transport-Security:` headers, this
bug can make the subdomain's expiry timeout *bleed over* and get set for the
parent domain `example.com` in curl's HSTS cache.

The result of a triggered bug is that HTTP accesses to `example.com` get
converted to HTTPS for a different period of time than what was asked for by
the origin server. If `example.com` for example stops supporting HTTPS at its
expiry time, curl might then fail to access `http://example.com` until the
(wrongly set) timeout expires. This bug can also expire the parent's entry
*earlier*, thus making curl inadvertently switch back to insecure HTTP earlier
than otherwise intended.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-9681

# [M] When curl is asked to use HSTS, the expiry time for a subdomain might overwrite a parent domain's...

## Summary
Severity: Medium
Advisory: JLSEC-2026-419
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-419
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.11.0+0
- Julia: `LibCURL_jll` — affected >=7.81.0+0 <8.11.0+0

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
- http://seclists.org/fulldisclosure/2025/Apr/10
- http://seclists.org/fulldisclosure/2025/Apr/11
- http://seclists.org/fulldisclosure/2025/Apr/12
- http://seclists.org/fulldisclosure/2025/Apr/13
- http://seclists.org/fulldisclosure/2025/Apr/4
- http://seclists.org/fulldisclosure/2025/Apr/5
- http://seclists.org/fulldisclosure/2025/Apr/8
- http://seclists.org/fulldisclosure/2025/Apr/9
- http://www.openwall.com/lists/oss-security/2024/11/06/2
- https://curl.se/docs/CVE-2024-9681.html
- https://curl.se/docs/CVE-2024-9681.json
- https://github.com/advisories/GHSA-g337-g667-mjvw
- https://hackerone.com/reports/2764830
- https://nvd.nist.gov/vuln/detail/CVE-2024-9681
- https://security.netapp.com/advisory/ntap-20241213-0006
- https://security.netapp.com/advisory/ntap-20241213-0006/

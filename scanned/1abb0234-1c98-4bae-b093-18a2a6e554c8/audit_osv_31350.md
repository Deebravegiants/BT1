# [M] HSTS subdomain overwrites parent cache entry

## Summary
Severity: Medium
Advisory: CVE-2024-9681
Aliases: CURL-CVE-2024-9681
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-11-06
Source: https://osv.dev/vulnerability/CVE-2024-9681
Type: osv

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
- https://hackerone.com/reports/2764830
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/9xxx/CVE-2024-9681.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-9681
- https://security.netapp.com/advisory/ntap-20241213-0006/

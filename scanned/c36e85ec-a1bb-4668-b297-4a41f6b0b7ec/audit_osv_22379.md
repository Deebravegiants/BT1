# [H] CVE-2022-27924

## Summary
Severity: High
Advisory: CVE-2022-27924
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-04-20
Source: https://osv.dev/vulnerability/CVE-2022-27924
Type: osv

## Details
Zimbra Collaboration (aka ZCS) 8.8.15 and 9.0 allows an unauthenticated attacker to inject arbitrary memcache commands into a targeted instance. These memcache commands becomes unescaped, causing an overwrite of arbitrary cached entries.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/9.0.0/P24
- https://wiki.zimbra.com/wiki/Zimbra_Security_Advisories
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2022-27924
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/27xxx/CVE-2022-27924.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-27924

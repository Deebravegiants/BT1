# [M] Password Pusher's rate limiter can be bypassed by forging proxy headers

## Summary
Severity: Medium
Advisory: CVE-2024-52796
Aliases: GHSA-ffp2-8p2h-4m5j
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-11-20
Source: https://osv.dev/vulnerability/CVE-2024-52796
Type: osv

## Details
Password Pusher, an open source application to communicate sensitive information over the web, comes with a configurable rate limiter.  In versions prior to v1.49.0, the rate limiter could be bypassed by forging proxy headers allowing bad actors to send unlimited traffic to the site potentially causing a denial of service. In v1.49.0, a fix was implemented to only authorize proxies on local IPs which resolves this issue. As a workaround, one may add rules to one's proxy and/or firewall to not accept external proxy headers such as `X-Forwarded-*` from clients.

## References
- https://docs.pwpush.com/docs/proxies/#trusted-proxies
- https://github.com/pglombardo/PasswordPusher/releases/tag/v1.49.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52796.json
- https://github.com/pglombardo/PasswordPusher/security/advisories/GHSA-ffp2-8p2h-4m5j
- https://nvd.nist.gov/vuln/detail/CVE-2024-52796

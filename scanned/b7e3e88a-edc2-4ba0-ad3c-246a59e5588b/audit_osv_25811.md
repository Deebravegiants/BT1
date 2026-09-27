# [M] Rate limiter not working reliable when Memcached is installed in Nextcloud

## Summary
Severity: Medium
Advisory: CVE-2023-45148
Aliases: GHSA-xmhp-7vr4-hp63
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-45148
Type: osv

## Details
Nextcloud is an open source home cloud server. When Memcached is used as `memcache.distributed` the rate limiting in Nextcloud Server could be reset unexpectedly resetting the rate count earlier than intended. Users are advised to upgrade to versions 25.0.11, 26.0.6 or 27.1.0. Users unable to upgrade should change their config setting `memcache.distributed` to `\OC\Memcache\Redis` and install Redis instead of Memcached.

## References
- https://hackerone.com/reports/2110945
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45148.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-xmhp-7vr4-hp63
- https://nvd.nist.gov/vuln/detail/CVE-2023-45148
- https://github.com/nextcloud/server/pull/40293

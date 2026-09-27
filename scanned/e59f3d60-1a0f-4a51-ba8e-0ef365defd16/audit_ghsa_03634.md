# [M] A poorly-behaved client could use keepalive requests to monopolize Puma's reactor and create a denial of service attack

## Summary
Severity: Medium
Advisory: GHSA-7xx3-m584-x994
CVE: CVE-2019-16770
CWE: CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2019-12-05
Source: https://github.com/advisories/GHSA-7xx3-m584-x994
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=0 <3.12.2
- RubyGems: `puma` — affected >=4.0.0 <4.3.1

## Details
## Keepalive thread overload/DoS

### Impact

A poorly-behaved client could use keepalive requests to monopolize Puma's reactor and create a denial of service attack.

If more keepalive connections to Puma are opened than there are threads available, additional connections will wait permanently if the attacker sends requests frequently enough.

### Patches

This vulnerability is patched in Puma 4.3.1 and 3.12.2.

### Workarounds

Reverse proxies in front of Puma could be configured to always allow less than X keepalive connections to a Puma cluster or process, where X is the number of threads configured in Puma's thread pool.

### For more information

If you have any questions or comments about this advisory:

* Open an issue at [puma](github.com/puma/puma).

## References
- https://github.com/puma/puma/security/advisories/GHSA-7xx3-m584-x994
- https://nvd.nist.gov/vuln/detail/CVE-2019-16770
- https://github.com/advisories/GHSA-7xx3-m584-x994
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2019-16770.yml
- https://lists.debian.org/debian-lts-announce/2022/05/msg00034.html

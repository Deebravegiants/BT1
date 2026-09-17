# [H] Missing Release of Memory after Effective Lifetime in Bareos Director

## Summary
Severity: High
Advisory: CVE-2022-24756
Aliases: GHSA-jh55-4wgw-xc9j
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-24756
Type: osv

## Details
Bareos is open source software for backup, archiving, and recovery of data for operating systems. When Bareos Director >= 18.2 but prior to 21.1.0, 20.0.6, and 19.2.12 is built and configured for PAM authentication, a failed PAM authentication will leak a small amount of memory. An attacker that is able to use the PAM Console (i.e. by knowing the shared secret or via the WebUI) can flood the Director with failing login attempts which will eventually lead to an out-of-memory condition in which the Director will not work anymore. Bareos Director versions 21.1.0, 20.0.6 and 19.2.12 contain a Bugfix for this problem. Users who are unable to upgrade may disable PAM authentication as a workaround.

## References
- https://huntr.dev/bounties/480121f2-bc3c-427e-986e-5acffb1606c5/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24756.json
- https://github.com/bareos/bareos/security/advisories/GHSA-jh55-4wgw-xc9j
- https://nvd.nist.gov/vuln/detail/CVE-2022-24756
- https://github.com/bareos/bareos/pull/1115
- https://github.com/bareos/bareos/pull/1119
- https://github.com/bareos/bareos/pull/1121

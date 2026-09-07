# [M] Cobbler Path Traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-xc7w-jvhx-p6q9
CVE: CVE-2014-3225
CWE: CWE-22
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xc7w-jvhx-p6q9
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=2.6.0 <2.6.4
- PyPI: `cobbler` — affected >=2.4.0 <2.4.7

## Details
Absolute path traversal vulnerability in the web interface in Cobbler 2.4.x through 2.6.x allows remote authenticated users to read arbitrary files via the Kickstart field in a profile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3225
- https://github.com/cobbler/cobbler/issues/939
- https://github.com/cobbler/cobbler/commit/8232c0e88ec7382d3f8d3bf48c81a4a91ac4325d
- https://github.com/cobbler/cobbler/commit/f757e3096fcd32397609ca38efb01f19d16dd634
- https://github.com/cobbler/cobbler
- https://www.youtube.com/watch?v=vuBaoQUFEYQ&feature=youtu.be
- http://packetstormsecurity.com/files/126553/Cobbler-Local-File-Inclusion.html
- http://seclists.org/oss-sec/2014/q2/273
- http://seclists.org/oss-sec/2014/q2/274
- http://www.exploit-db.com/exploits/33252
- http://www.osvdb.org/106759
- http://www.securityfocus.com/archive/1/532094/100/0/threaded
- http://www.securityfocus.com/bid/67277

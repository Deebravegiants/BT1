# [C] dns-sync command injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-q5pq-pgrv-fh89
CVE: CVE-2014-9682
CWE: CWE-77
Ecosystem: npm
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-q5pq-pgrv-fh89
Type: github-advisory

## Affected
- npm: `dns-sync` — affected >=0 <0.1.1

## Details
The dns-sync module before 0.1.1 for node.js allows context-dependent attackers to execute arbitrary commands via shell metacharacters in the first argument to the resolve API function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-9682
- https://github.com/skoranga/node-dns-sync/issues/1
- https://github.com/skoranga/node-dns-sync/commit/d9abaae384b198db1095735ad9c1c73d7b890a0d
- https://github.com/advisories/GHSA-q5pq-pgrv-fh89
- https://github.com/skoranga/node-dns-sync
- http://www.openwall.com/lists/oss-security/2014/11/11/6

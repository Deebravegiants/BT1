# [C] Command Injection in dns-sync

## Summary
Severity: Critical
Advisory: GHSA-jcw8-r9xm-32c6
CVE: CVE-2017-16100
CWE: CWE-94
Ecosystem: npm
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-jcw8-r9xm-32c6
Type: github-advisory

## Affected
- npm: `dns-sync` — affected >=0 <0.1.1

## Details
Affected versions of `dns-sync` have an arbitrary command execution vulnerability in the `resolve()` method. 



## Recommendation

- Use an alternative dns resolver
- Do not allow untrusted input into `dns-sync.resolve()`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16100
- https://github.com/skoranga/node-dns-sync/issues/1
- https://github.com/skoranga/node-dns-sync/issues/1)
- https://github.com/skoranga/node-dns-sync/issues/5
- https://github.com/skoranga/node-dns-sync/commit/d9abaae384b198db1095735ad9c1c73d7b890a0d
- https://github.com/skoranga/node-dns-sync/commit/d9abaae384b198db1095735ad9c1c73d7b890a0d)))
- https://github.com/advisories/GHSA-jcw8-r9xm-32c6
- https://www.npmjs.com/advisories/153
- https://www.npmjs.com/advisories/523

# [H] Downloads Resources over HTTP in imageoptim

## Summary
Severity: High
Advisory: GHSA-mm7h-323r-9p4g
CVE: CVE-2016-10596
CWE: CWE-311
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-mm7h-323r-9p4g
Type: github-advisory

## Affected
- npm: `imageoptim` — affected >=0

## Details
imageoptim is a Node.js wrapper for some images compression algorithms.

imageoptim downloads zipped resources over HTTP, which leaves it vulnerable to MITM attacks.  It may be possible to cause remote code execution (RCE) by swapping out the requested tarball with an attacker controlled tarball if the attacker is on the network or positioned in between the user and the remote server.


## Recommendation

No fix is currently available for this vulnerability.

It is our recommendation to not install or use this module at this time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10596
- https://github.com/advisories/GHSA-mm7h-323r-9p4g
- https://www.npmjs.com/advisories/194

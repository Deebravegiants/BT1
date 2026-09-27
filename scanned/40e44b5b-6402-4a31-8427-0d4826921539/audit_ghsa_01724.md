# [H] Insecure Entropy Source - Math.random() in node-uuid

## Summary
Severity: High
Advisory: GHSA-265q-28rp-chq5
CVE: CVE-2015-8851
CWE: CWE-331
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-04-16
Source: https://github.com/advisories/GHSA-265q-28rp-chq5
Type: github-advisory

## Affected
- npm: `node-uuid` — affected >=0 <1.4.4

## Details
Affected versions of `node-uuid` consistently fall back to using `Math.random` as an entropy source instead of `crypto`, which may result in guessable UUID's.



## Recommendation

Update to version 1.4.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8851
- https://github.com/broofa/node-uuid/issues/108
- https://github.com/broofa/node-uuid/issues/122
- https://github.com/broofa/node-uuid/commit/672f3834ed02c798aa021c618d0a5666c8da000d
- https://bugzilla.redhat.com/show_bug.cgi?id=1327056
- https://www.npmjs.com/advisories/93
- http://www.openwall.com/lists/oss-security/2016/04/13/8

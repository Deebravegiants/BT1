# [H] Path traversal attack on Windows platforms

## Summary
Severity: High
Advisory: GHSA-89r3-rcpj-h7w6
CVE: CVE-2019-0207
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-11-18
Source: https://github.com/advisories/GHSA-89r3-rcpj-h7w6
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-core` — affected >=5.4.0 <5.4.5

## Details
Tapestry processes assets `/assets/ctx` using classes chain `StaticFilesFilter -> AssetDispatcher -> ContextResource`, which doesn't filter the character `\`, so attacker can perform a path traversal attack to read any files on Windows platform.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0207
- https://lists.apache.org/thread.html/765be3606d865de513f6df9288842c3cf58b09a987c617a535f2b99d@%3Cusers.tapestry.apache.org%3E
- https://lists.apache.org/thread.html/bac8d6f9e1b4059b319d9cba6f33219a99b81623476ec896138f851c@%3Cusers.tapestry.apache.org%3E
- https://lists.apache.org/thread.html/r7d9c54beb1dc97dcccc58d9b5d31f0f7166f9a25ad1beba5f8091e0c@%3Ccommits.tapestry.apache.org%3E
- https://lists.apache.org/thread.html/r87523dd07886223aa086edc25fe9b8ddb9c1090f7db25b068dc30843@%3Ccommits.tapestry.apache.org%3E

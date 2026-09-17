# [H] Downloads Resources over HTTP in apk-parser

## Summary
Severity: High
Advisory: GHSA-5g4r-87v2-jqvx
CVE: CVE-2016-10564
CWE: CWE-311
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-5g4r-87v2-jqvx
Type: github-advisory

## Affected
- npm: `apk-parser` — affected >=0 <0.1.6

## Details
apk-parser is a tool to extract Android Manifest info from an APK file.

apk-parser versions below 0.1.6 download binary resources over HTTP, which leaves it vulnerable to MITM attacks.  It may be possible to cause remote code execution (RCE) by swapping out the requested binary with an attacker controlled binary if the attacker is on the network or positioned in between the user and the remote server.


## Recommendation

Update to version 0.1.6 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10564
- https://www.npmjs.com/advisories/195

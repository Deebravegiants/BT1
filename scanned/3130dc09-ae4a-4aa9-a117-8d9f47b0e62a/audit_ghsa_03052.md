# [H] Command Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-2m8v-572m-ff2v
CVE: CVE-2021-21315
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H/E:H (CVSS_V3)
Published: 2021-02-16
Source: https://github.com/advisories/GHSA-2m8v-572m-ff2v
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <5.3.1

## Details
### Impact
command injection vulnerability

### Patches
Problem was fixed with a parameter check. Please upgrade to version >= 5.3.1

### Workarounds
If you cannot upgrade, be sure to check or sanitize service parameters that are passed to si.inetLatency(), si.inetChecksite(), si.services(), si.processLoad() ... do only allow strings, reject any arrays. String sanitation works as expected.

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-2m8v-572m-ff2v
- https://nvd.nist.gov/vuln/detail/CVE-2021-21315
- https://github.com/sebhildebrandt/systeminformation/commit/07daa05fb06f24f96297abaa30c2ace8bfd8b525
- https://github.com/sebhildebrandt/systeminformation
- https://lists.apache.org/thread.html/r8afea9a83ed568f2647cccc6d8d06126f9815715ddf9a4d479b26b05%40%3Cissues.cordova.apache.org%3E
- https://lists.apache.org/thread.html/r8afea9a83ed568f2647cccc6d8d06126f9815715ddf9a4d479b26b05@%3Cissues.cordova.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210312-0007
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-21315
- https://www.npmjs.com/package/systeminformation

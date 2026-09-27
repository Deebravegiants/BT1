# [H] steroids downloads resources over HTTP

## Summary
Severity: High
Advisory: GHSA-5m9c-634g-47vq
CVE: CVE-2016-10581
CWE: CWE-311
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-5m9c-634g-47vq
Type: github-advisory

## Affected
- npm: `steroids` — affected >=0

## Details
Affected versions of `steroids` insecurely download an executable over an unencrypted HTTP connection. 

In scenarios where an attacker has a privileged network position, it is possible to intercept the response and replace the executable with a malicious one, resulting in code execution on the system running `steroids`.


## Recommendation

This vulnerability was discovered and reported in 2016, yet has not seen a patch issued as of 03/2018. As of 08/2022, [the package is marked as deprecated](https://www.npmjs.com/package/steroids) and the GitHub repository is no longer publicly available.

The best path forward for mitigating this issue is to attempt to use an alternative module that is actively maintained and which provides similar functionality, such as the native PhoneGap API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10581
- https://github.com/AppGyver/steroids
- https://github.com/AppGyver/steroids/blob/master/package.json#L101
- https://github.com/AppGyver/steroids/blob/master/package.json#L103-L104
- https://github.com/AppGyver/steroids/blob/master/package.json#L74
- https://www.npmjs.com/advisories/168

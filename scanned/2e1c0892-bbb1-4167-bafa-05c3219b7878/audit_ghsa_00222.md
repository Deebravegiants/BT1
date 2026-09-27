# [H] Regular Expression Denial of Service in string package

## Summary
Severity: High
Advisory: GHSA-g36h-6r4f-3mqp
CVE: CVE-2017-16116
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-g36h-6r4f-3mqp
Type: github-advisory

## Affected
- npm: `string` — affected >=0

## Details
Affected versions of `string` are vulnerable to regular expression denial of service when specifically crafted untrusted user input is passed into the `underscore` or `unescapeHTML` methods.


## Recommendation

There is currently no direct patch for this vulnerability. 

Currently, the best solution is to avoid passing user input to the `underscore` and `unescapeHTML` methods.

Alternatively, a user provided patch is available in [Pull Request #217]( https://github.com/jprichardson/string.js/pull/217/commits/eab9511e4efbc8c521e18b6cf2e8565ae50c5a16), however this patch has not been tested, nor has it been merged by the package author.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16116
- https://github.com/jprichardson/string.js/issues/212
- https://github.com/advisories/GHSA-g36h-6r4f-3mqp
- https://www.npmjs.com/advisories/536

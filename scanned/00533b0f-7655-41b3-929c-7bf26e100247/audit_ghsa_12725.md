# [M] mel-spintax has Inefficient Regular Expression Complexity

## Summary
Severity: Medium
Advisory: GHSA-qjm7-55vv-3c5f
CVE: CVE-2018-25077
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-qjm7-55vv-3c5f
Type: github-advisory

## Affected
- npm: `mel-spintax` — affected >=0 <1.0.3

## Details
A vulnerability was found in melnaron mel-spintax. It has been rated as problematic. Affected by this issue is some unknown functionality of the file `lib/spintax.js`. The manipulation of the argument text leads to inefficient regular expression complexity. The name of the patch is 37767617846e27b87b63004e30216e8f919637d3. It is recommended to apply a patch to fix this issue. The identifier of this vulnerability is VDB-218456.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-25077
- https://github.com/melnaron/mel-spintax/commit/37767617846e27b87b63004e30216e8f919637d3
- https://github.com/melnaron/mel-spintax
- https://vuldb.com/?id.218456

# [H] Regular Expression Denial of Service in tough-cookie

## Summary
Severity: High
Advisory: GHSA-g7q5-pjjr-gqvp
CVE: CVE-2017-15010
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-g7q5-pjjr-gqvp
Type: github-advisory

## Affected
- npm: `tough-cookie` — affected >=0 <2.3.3

## Details
Affected versions of `tough-cookie` are susceptible to a regular expression denial of service.

The amplification on this vulnerability is relatively low - it takes around 2 seconds for the engine to execute on a malicious input which is 50,000 characters in length.

If node was compiled using the `-DHTTP_MAX_HEADER_SIZE` however, the impact of the vulnerability can be significant, as the primary limitation for the vulnerability is the default max HTTP header length in node.


## Recommendation

Update to version 2.3.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15010
- https://github.com/salesforce/tough-cookie/issues/92
- https://github.com/salesforce/tough-cookie/commit/f1ed420a6a92ea7a5418df6e39e676556bc0c71d
- https://access.redhat.com/errata/RHSA-2017:2912
- https://access.redhat.com/errata/RHSA-2017:2913
- https://access.redhat.com/errata/RHSA-2018:1263
- https://access.redhat.com/errata/RHSA-2018:1264
- https://github.com/advisories/GHSA-g7q5-pjjr-gqvp
- https://github.com/salesforce/tough-cookie
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6VEBDTGNHVM677SLZDEHMWOP3ISMZSFT
- https://snyk.io/vuln/npm:tough-cookie:20170905
- https://www.npmjs.com/advisories/525
- http://www.securityfocus.com/bid/101185

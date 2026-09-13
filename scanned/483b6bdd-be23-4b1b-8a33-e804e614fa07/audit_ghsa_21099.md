# [H] Apache Tapestry 5.8.1 vulnerable to ReDoS via Content Types causing catastrophic backtracking

## Summary
Severity: High
Advisory: GHSA-227g-7cvv-6ff3
CVE: CVE-2022-31781
CWE: CWE-1333, CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-14
Source: https://github.com/advisories/GHSA-227g-7cvv-6ff3
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-core` — affected >=0 <5.8.2

## Details
Apache Tapestry up to version 5.8.1 is vulnerable to Regular Expression Denial of Service (ReDoS) in the way it handles Content Types. Specially crafted Content Types may cause catastrophic backtracking, taking exponential time to complete. Specifically, this is about the regular expression used on the parameter of the org.apache.tapestry5.http.ContentType class. Apache Tapestry 5.8.2 has a fix for this vulnerability. Notice the vulnerability cannot be triggered by web requests in Tapestry code alone. It would only happen if there's some non-Tapestry codepath passing some outside input to the ContentType class constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-31781
- https://github.com/apache/tapestry-5/commit/3c8d6103832eec3bc06029dd2532f06df717431f
- https://www.openwall.com/lists/oss-security/2022/07/12/3

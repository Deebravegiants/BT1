# [M] CVE-2020-26256

## Summary
Severity: Medium
Advisory: CVE-2020-26256
Aliases: GHSA-8cv5-p934-3hwp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-12-08
Source: https://osv.dev/vulnerability/CVE-2020-26256
Type: osv

## Details
Fast-csv is an npm package for parsing and formatting CSVs or any other delimited value file in node. In fast-cvs before version 4.3.6 there is a possible ReDoS vulnerability (Regular Expression Denial of Service) when using ignoreEmpty option when parsing. This has been patched in `v4.3.6` You will only be affected by this if you use the `ignoreEmpty` parsing option. If you do use this option it is recommended that you upgrade to the latest version `v4.3.6` This vulnerability was found using a CodeQL query which identified `EMPTY_ROW_REGEXP` regular expression as vulnerable.

## References
- https://www.npmjs.com/package/%40fast-csv/parse
- https://github.com/C2FO/fast-csv/issues/540
- https://github.com/C2FO/fast-csv/security/advisories/GHSA-8cv5-p934-3hwp
- https://www.npmjs.com/package/fast-csv
- https://github.com/C2FO/fast-csv/commit/4bbd39f26a8cd7382151ab4f5fb102234b2f829e
- https://lgtm.com/query/8609731774537641779/

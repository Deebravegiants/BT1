# [H] CVE-2021-23382

## Summary
Severity: High
Advisory: CVE-2021-23382
Aliases: GHSA-566m-qj78-rww5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-26
Source: https://osv.dev/vulnerability/CVE-2021-23382
Type: osv

## Details
The package postcss before 8.2.13 are vulnerable to Regular Expression Denial of Service (ReDoS) via getAnnotationURL() and loadAnnotation() in lib/previous-map.js. The vulnerable regexes are caused mainly by the sub-pattern \/\*\s* sourceMappingURL=(.*).

## References
- https://github.com/postcss/postcss/commit/2b1d04c867995e55124e0a165b7c6622c1735956
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1255641
- https://snyk.io/vuln/SNYK-JS-POSTCSS-1255640

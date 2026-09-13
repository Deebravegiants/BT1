# [M] Angular: Denial of Service (DoS) via OOM in Number Formatting (digitsInfo)

## Summary
Severity: Medium
Advisory: CVE-2026-50171
Aliases: GHSA-p3vc-36g9-x9gr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2026-50171
Type: osv

## Details
Angular is a development platform for building mobile and desktop web applications using TypeScript/JavaScript and other languages. Prior to 22.0.0-rc.2, 21.2.15, 20.3.22, and 19.2.23, a Denial of Service (DoS) vulnerability exists in the @angular/common package of Angular. The formatNumber function, which is also utilized by DecimalPipe, PercentPipe, and CurrencyPipe, does not properly validate the upper bounds of the digitsInfo parameter. Specifically, the minimum and maximum fraction digits parsed from the digitsInfo string (e.g., 1.2-4) are converted to integers and used without limits. When parsing a maliciously crafted digitsInfo string with excessively large fraction digit values (e.g., 1.200000000-200000000), the internal roundNumber function attempts to pad the digits array to match the requested fraction size. This results in an unbounded loop that repeatedly pushes elements into an array.  This vulnerability is fixed in 22.0.0-rc.2, 21.2.15, 20.3.22, and 19.2.23.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50171.json
- https://github.com/angular/angular/security/advisories/GHSA-p3vc-36g9-x9gr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50171

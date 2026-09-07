# [M] Apache ECharts has a cross-site scripting (XSS) vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fgmj-fm8m-jvvx
CVE: CVE-2026-45249
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-fgmj-fm8m-jvvx
Type: github-advisory

## Affected
- npm: `echarts` — affected >=0 <6.1.0

## Details
A cross-site scripting (XSS) vulnerability exists in Apache ECharts in the Lines series tooltip rendering logic.

This issue affects Apache ECharts: from before 6.1.0.

In versions prior to 6.1.0, if both Lines series and tooltip are used, and no user-specified tooltip.formatter is provided, and series.data[i].name is specified, raw HTML string series.data[i].name can be rendered through innerHTML sink into tooltip content. Although tooltip is allowed to accept user-provided raw HTML via a custom tooltip.formatter, the built-in tooltip formatters conventionally perform HTML escaping automatically. This case breaks that convention and may unexpectedly lead to script execution when tooltips are displayed.


Users are recommended to upgrade to version 6.1.0 if using the Lines series in this way, which fixes the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-45249
- https://github.com/apache/echarts/pull/21608
- https://github.com/apache/echarts/commit/1e39b00eedda0e4a0b048e099c0e13ce7149d90f
- https://echarts.apache.org/en/option.html#series-lines
- https://echarts.apache.org/handbook/en/best-practices/security/#passing_raw_html_safely
- https://github.com/apache/echarts
- https://lists.apache.org/thread/1g6xk7gd9vg1c6zyqqt2lnko10zomc3o
- http://www.openwall.com/lists/oss-security/2026/05/23/4

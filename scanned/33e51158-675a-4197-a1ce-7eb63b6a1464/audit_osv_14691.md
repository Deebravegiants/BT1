# [C] CVE-2019-10807

## Summary
Severity: Critical
Advisory: CVE-2019-10807
Aliases: GHSA-8cxp-cjm8-fj36
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-11
Source: https://osv.dev/vulnerability/CVE-2019-10807
Type: osv

## Details
Blamer versions prior to 1.0.1 allows execution of arbitrary commands. It is possible to inject arbitrary commands as part of the arguments provided to blamer.

## References
- https://github.com/kucherenko/blamer/commit/5fada8c9b6986ecd28942b724fa682e77ce1e11c%2C
- https://snyk.io/vuln/SNYK-JS-BLAMER-559541

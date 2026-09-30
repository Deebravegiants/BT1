# [M] CVE-2020-7600

## Summary
Severity: Medium
Advisory: CVE-2020-7600
Aliases: GHSA-2cf2-2383-h4jv, SNYK-JS-QUERYMEN-559867
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2020-03-12
Source: https://osv.dev/vulnerability/CVE-2020-7600
Type: osv

## Details
querymen prior to 2.1.4 allows modification of object properties. The parameters of exported function handler(type, name, fn) can be controlled by users without any sanitization. This could be abused for Prototype Pollution attacks.

## References
- https://snyk.io/vuln/SNYK-JS-QUERYMEN-559867
- https://github.com/diegohaz/querymen/commit/1987fefcb3b7508253a29502a008d5063a873cef

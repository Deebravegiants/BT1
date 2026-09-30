# [M] CVE-2017-16008

## Summary
Severity: Medium
Advisory: CVE-2017-16008
Aliases: GHSA-f89g-whpf-6q9m
CVSS: 6.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2017-16008
Type: osv

## Details
i18next is a language translation framework. Because of how the interpolation is implemented, making replacements from the dictionary one at a time, untrusted user input can use the name of one of the dictionary keys to inject script into the browser. This affects i18next <=1.10.2.

## References
- https://github.com/i18next/i18next/pull/443
- https://nodesecurity.io/advisories/325

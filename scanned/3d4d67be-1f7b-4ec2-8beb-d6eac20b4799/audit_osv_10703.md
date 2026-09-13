# [M] CVE-2017-18350

## Summary
Severity: Medium
Advisory: CVE-2017-18350
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-12
Source: https://osv.dev/vulnerability/CVE-2017-18350
Type: osv

## Details
bitcoind and Bitcoin-Qt prior to 0.15.1 have a stack-based buffer overflow if an attacker-controlled SOCKS proxy server is used. This results from an integer signedness error when the proxy server responds with an acknowledgement of an unexpected target domain name.

## References
- https://medium.com/%40lukedashjr/cve-2017-18350-disclosure-fe6d695f45d5
- https://en.bitcoin.it/wiki/Common_Vulnerabilities_and_Exposures

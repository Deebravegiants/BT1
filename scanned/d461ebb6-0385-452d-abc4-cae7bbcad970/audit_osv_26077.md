# [C] CVE-2023-50694

## Summary
Severity: Critical
Advisory: CVE-2023-50694
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-19
Source: https://osv.dev/vulnerability/CVE-2023-50694
Type: osv

## Details
An issue in dom96 HTTPbeast v.0.4.1 and before allows a remote attacker to send a malicious crafted request due to insufficient parsing in the parser.nim component.

## References
- https://gist.github.com/anas-cherni/c95e2fc1fd84d93167eb60193318d0b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50694.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-50694
- https://github.com/dom96/httpbeast/issues/95
- https://github.com/dom96/httpbeast/pull/96

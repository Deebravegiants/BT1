# [H] CVE-2022-32984

## Summary
Severity: High
Advisory: CVE-2022-32984
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-31
Source: https://osv.dev/vulnerability/CVE-2022-32984
Type: osv

## Details
BTCPay Server 1.3.0 through 1.5.3 allows a remote attacker to obtain sensitive information when a public Point of Sale app is exposed. The sensitive information, found in the HTML source code, includes the xpub of the store. Also, if the store isn't using the internal lightning node, the credentials of a lightning node are exposed.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32984.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32984
- https://blog.btcpayserver.org/btcpay-server-cve-2022-32984/

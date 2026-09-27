# [H] CardGate Payments plugin for WooCommerce does not validate request origin

## Summary
Severity: High
Advisory: GHSA-5pq5-9phv-q5j3
CVE: CVE-2020-8819
CWE: CWE-346
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5pq5-9phv-q5j3
Type: github-advisory

## Affected
- Packagist: `cardgate/woocommerce` — affected >=0 <3.1.16

## Details
An issue was discovered in the CardGate Payments plugin through 3.1.15 for WooCommerce. Lack of origin authentication in the IPN callback processing function in cardgate/cardgate.php allows an attacker to remotely replace critical plugin settings (merchant ID, secret key, etc.) and therefore bypass the payment process (e.g., spoof an order status by manually sending an IPN callback request with a valid signature but without real payment) and/or receive all of the subsequent payments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8819
- https://github.com/cardgate/woocommerce/issues/18
- https://github.com/cardgate/woocommerce/pull/17/commits/0b83588d604c8c56c7fded43144fcced96b2ada9
- https://github.com/cardgate/woocommerce
- https://github.com/cardgate/woocommerce/blob/f2111af7b1a3fd701c1c5916137f3ac09482feeb/cardgate/cardgate.php#L426-L442
- https://wpvulndb.com/vulnerabilities/10097
- https://www.exploit-db.com/exploits/48134
- http://packetstormsecurity.com/files/156504/WordPress-WooCommerce-CardGate-Payment-Gateway-3.1.15-Bypass.html

# [H] Origin Validation Error in Magento 2

## Summary
Severity: High
Advisory: GHSA-qf6q-qfwp-vp44
CVE: CVE-2020-8818
CWE: CWE-346
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-qf6q-qfwp-vp44
Type: github-advisory

## Affected
- Packagist: `cardgate/magento2` — affected >=0 <2.0.33

## Details
An issue was discovered in the CardGate Payments plugin through 2.0.30 for Magento 2. Lack of origin authentication in the IPN callback processing function in Controller/Payment/Callback.php allows an attacker to remotely replace critical plugin settings (merchant ID, secret key, etc.) and therefore bypass the payment process (e.g., spoof an order status by manually sending an IPN callback request with a valid signature but without real payment) and/or receive all of the subsequent payments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8818
- https://github.com/cardgate/magento2/issues/54
- https://github.com/cardgate/magento2
- https://github.com/cardgate/magento2/blob/715979e54e1a335d78a8c5586f9e9987c3bf94fd/Controller/Payment/Callback.php#L88-L107
- https://github.com/cardgate/magento2/releases/tag/v2.0.33
- http://packetstormsecurity.com/files/156505/Magento-WooCommerce-CardGate-Payment-Gateway-2.0.30-Bypass.html

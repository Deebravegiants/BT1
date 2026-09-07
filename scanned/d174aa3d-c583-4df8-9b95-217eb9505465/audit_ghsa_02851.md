# [H] Sylius PayPal Plugin allows unauthorized access to Credit card form, exposing payer name and not requiring 3DS

## Summary
Severity: High
Advisory: GHSA-25fx-mxc2-76g7
CVE: CVE-2021-41120
CWE: CWE-200, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-25fx-mxc2-76g7
Type: github-advisory

## Affected
- Packagist: `sylius/paypal-plugin` — affected >=1.0.0 <1.2.4
- Packagist: `sylius/paypal-plugin` — affected >=1.3.0 <1.3.1

## Details
### Impact
URL to the payment page done after checkout was created with autoincremented payment id (`/pay-with-paypal/{id}`) and therefore it was easy to access for anyone, not even the order's customer. The problem was, the Credit card form has prefilled "credit card holder" field with the Customer's first and last name.
Additionally, the mentioned form did not require a 3D Secure authentication, as well as did not checked the result of the 3D Secure authentication.

### Patches
The problem has been patched in Sylius/PayPalPlugin **1.2.4** and **1.3.1**

### Workarounds
One can override a `sylius_paypal_plugin_pay_with_paypal_form` route and change its URL parameters to (for example) `{orderToken}/{paymentId}`, then override the `Sylius\PayPalPlugin\Controller\PayWithPayPalFormAction` service, to operate on the payment taken from the repository by these 2 values. It would also require usage of custom repository method.
Additionally, one could override the `@SyliusPayPalPlugin/payWithPaypal.html.twig` template, to add `contingencies: ['SCA_ALWAYS']` line in `hostedFields.submit(...)` function call (line 421). It would then have to be handled in the function callback.

### For more information
If you have any questions or comments about this advisory:
- Open an issue in Sylius/PayPalPlugin issues
- Email us at security at sylius dot com

## References
- https://github.com/Sylius/PayPalPlugin/security/advisories/GHSA-25fx-mxc2-76g7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41120
- https://github.com/Sylius/PayPalPlugin/commit/2adc46be2764ccee22b4247139b8056fb8d1afff
- https://github.com/Sylius/PayPalPlugin/commit/814923c2e9d97fe6279dcee866c34ced3d2fb7a7
- https://github.com/Sylius/PayPalPlugin

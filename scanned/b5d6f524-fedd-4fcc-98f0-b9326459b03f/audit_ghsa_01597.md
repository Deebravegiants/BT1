# [M] Ability to switch customer email address on account detail page and stay verified

## Summary
Severity: Medium
Advisory: GHSA-6gw4-x63h-5499
CVE: CVE-2020-15245
CWE: CWE-79, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2020-10-19
Source: https://github.com/advisories/GHSA-6gw4-x63h-5499
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=1.7.0 <1.7.9
- Packagist: `sylius/sylius` — affected >=1.8.0 <1.8.3
- Packagist: `sylius/sylius` — affected >=1.0.0 <1.6.9

## Details
### Impact
The user may register in a shop by email mail@example.com, verify it, change it to the mail another@domain.com and stay verified and enabled. This may lead to having accounts addressed to totally different emails, that were verified. Note, that this way one is not able to take over any existing account (guest or normal one).

### Patches
Patch has been provided for Sylius 1.6.x and newer - 1.6.9, 1.7.9, 1.8.3. Versions older than 1.6 are not covered by our security support anymore.

### Workarounds
If for whatever reason you are not able to upgrade your application version, you may resolve this issue on your own by creating a custom event listener, which will listen to the `sylius.customer.pre_update` event. You can determine that email has been changed if customer email and user username are different. They are synchronized later on. Pay attention, to email changing behavior for administrators. You may need to skip this logic for them. In order to achieve this, you should either check master request path info, if it does not contain `/admin` prefix or adjust event triggered during customer update in the shop. You can find more information on how to customize the event here.

### Acknowledgements

This security issue has been reported by Mircea Silviu (@decemvre), thanks a lot!

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-6gw4-x63h-5499
- https://nvd.nist.gov/vuln/detail/CVE-2020-15245
- https://github.com/Sylius/Sylius/commit/60636d711a4011e8694d10d201b53632c7e8ecaf
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/sylius/CVE-2020-15245.yaml
- https://github.com/Sylius/Sylius

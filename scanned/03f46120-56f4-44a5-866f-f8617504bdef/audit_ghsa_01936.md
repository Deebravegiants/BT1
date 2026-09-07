# [M] List of order ids, number, items total and token value exposed for unauthorized uses via new API

## Summary
Severity: Medium
Advisory: GHSA-rpxh-vg2x-526v
CVE: CVE-2021-32720
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-rpxh-vg2x-526v
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=1.9.0 <1.9.5

## Details
### Impact

Part of the details (order ID, order number, items total, and token value) of all placed orders were exposed to unauthorized users. If exploited properly, a few additional information like the number of items in the cart and the date of the shipping may be fetched as well. This data seems to not be crucial nor is personal data, however, could be used for sociotechnical attacks or may expose a few details about shop condition to the third parties. The data possible to aggregate are the number of processed orders or their value in the moment of time. 

### Patches

The problem has been patched at Sylius 1.9.5 and 1.10.0

### Workarounds
There are a few ways to fix this without updating the code. 

The first possible solution is to hide the problematic endpoints behind the firewall from not logged in users. In order to achieve it one has to add the configuration in `config/packages/security.yaml`:
```yaml
    access_control:
        # ... 
        - { path: "%sylius.security.new_api_shop_regex%/orders", role: IS_AUTHENTICATED_ANONYMOUSLY, methods: [POST] }
        - { path: "%sylius.security.new_api_shop_regex%/orders", role: ROLE_USER, methods: [GET] }
```
This would put only the order list under the firewall and allow only authorized users to access it. Once a user is authorized, it will have access to theirs orders only.

The second possible solution is to decorate the `\Sylius\Bundle\ApiBundle\Doctrine\QueryCollectionExtension\OrdersByLoggedInUserExtension` and throw `Symfony\Component\Security\Core\Exception\AccessDeniedException` if the class is executed for unauthorized user.

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-rpxh-vg2x-526v
- https://nvd.nist.gov/vuln/detail/CVE-2021-32720
- https://github.com/Sylius/Sylius/commit/21d509851559230d03292b2a635a6951748c2758
- https://github.com/Sylius/Sylius/releases/tag/v1.9.5
- https://packagist.org/packages/sylius/sylius

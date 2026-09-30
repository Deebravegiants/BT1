# [H] Sylius has a security vulnerability via adjustments API endpoint

## Summary
Severity: High
Advisory: GHSA-55rf-8q29-4g43
CVE: CVE-2024-40633
CWE: CWE-200, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-55rf-8q29-4g43
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=1.12.0-alpha.1 <1.12.19
- Packagist: `sylius/sylius` — affected >=1.13.0-alpha.1 <1.13.4
- Packagist: `sylius/sylius` — affected >=0 <1.9.12
- Packagist: `sylius/sylius` — affected >=1.10.0-alpha.1 <1.10.16
- Packagist: `sylius/sylius` — affected >=1.11.0-alpha.1 <1.11.17

## Details
### Impact
A security vulnerability was discovered in the `/api/v2/shop/adjustments/{id}` endpoint, which retrieves order adjustments based on incremental integer IDs. The vulnerability allows an attacker to enumerate valid adjustment IDs and retrieve order tokens. Using these tokens, an attacker can access guest customer order details - sensitive guest customer information.

### Patches
The issue is fixed in versions: 1.9.12, 1.10.16, 1.11.17, 1.12.19, 1.13.4 and above.
The `/api/v2/shop/adjustments/{id}` will always return `404` status.

### Workarounds

Using YAML configuration:

Create `config/api_platform/Adjustment.yaml` file:

```yaml
# config/api_platform/Adjustment.yaml

'%sylius.model.adjustment.class%':
    itemOperations:
        shop_get:
            controller: ApiPlatform\Core\Action\NotFoundAction
            read: false
            output: false
```

Or using XML configuration:

> Note: This is the only way of disabling the vulnerable endpoint for Sylius 1.9, as YAML configuration is not supported in that version.

Copy the original configuration from vendor:

```bash
# create directory if it doesn't exist
mkdir -p config/api_platform

cp vendor/sylius/sylius/src/Sylius/Bundle/ApiBundle/Resources/config/api_resources/Adjustment.xml config/api_platform
```

And change the `shop_get` operation in copied `config/api_platform/Adjustment.xml` file:

```xml
<!-- config/api_platform/Adjustment.xml -->

...
<itemOperation name="shop_get">
    <attribute name="method">GET</attribute>
    <attribute name="path">/shop/adjustments/{id}</attribute>
    <attribute name="controller">ApiPlatform\Core\Action\NotFoundAction</attribute>
    <attribute name="read">false</attribute>
    <attribute name="output">false</attribute>
</itemOperation>
...
```

Update your API platform paths config if needed so the new configuration file is loaded:

```yaml
# config/packages/api_platform.yaml
api_platform:
    mapping:
        paths:
          - '%kernel.project_dir%/vendor/sylius/sylius/src/Sylius/Bundle/ApiBundle/Resources/config/api_resources'
          ...
          - '%kernel.project_dir%/config/api_platform'
```

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-55rf-8q29-4g43
- https://nvd.nist.gov/vuln/detail/CVE-2024-40633
- https://github.com/Sylius/Sylius/commit/d833b2871caa3b8d1f0a8207378bb778f0b90464
- https://github.com/Sylius/Sylius

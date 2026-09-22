# [M] Ability to expose data in Sylius by using an unintended serialisation group

## Summary
Severity: Medium
Advisory: GHSA-8vp7-j5cj-vvm2
CVE: CVE-2020-5220
CWE: CWE-200, CWE-444
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-01-31
Source: https://github.com/advisories/GHSA-8vp7-j5cj-vvm2
Type: github-advisory

## Affected
- Packagist: `sylius/resource-bundle` — affected >=1.4.0 <1.4.6
- Packagist: `sylius/resource-bundle` — affected >=1.5.0 <1.5.1
- Packagist: `sylius/resource-bundle` — affected >=1.6.0 <1.6.3
- Packagist: `sylius/sylius` — affected >=0 <1.3.12
- Packagist: `sylius/sylius` — affected >=1.4.0 <1.4.4
- Packagist: `sylius/resource-bundle` — affected >=1.0.0 <1.3.13

## Details
### Impact

ResourceBundle accepts and uses any serialisation groups to be passed via a HTTP header. This might lead to data exposure by using an unintended serialisation group - for example it could make Shop API use a more permissive group from Admin API.

Anyone exposing an API with ResourceBundle's controller is affected. The vulnerable versions are: `<1.3 || >=1.3.0 <=1.3.12 || >=1.4.0 <=1.4.5 || >=1.5.0 <=1.5.0 || >=1.6.0 <=1.6.2`.

### Patches

The patch is provided for ResourceBundle 1.3.13, 1.4.6, 1.5.1 and 1.6.3, but not for any versions below 1.3.

After it is applied, It allows to choose only the groups that are defined in `serialization_groups` or `allowed_serialization_groups` route definition. Any group not defined in those will not be used.

This behaviour might be a BC break for those using custom groups via the HTTP header, please adjust `allowed_serialization_groups` accordingly.

### Workarounds

Service `sylius.resource_controller.request_configuration_factory` can be overridden with an implementation copied from `\Sylius\Bundle\ResourceBundle\Controller\RequestConfigurationFactory` where the part that handles custom serialisation groups is deleted.

## References
- https://github.com/Sylius/SyliusResourceBundle/security/advisories/GHSA-8vp7-j5cj-vvm2
- https://nvd.nist.gov/vuln/detail/CVE-2020-5220
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/resource-bundle/CVE-2020-5220.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/sylius/CVE-2020-5220.yaml

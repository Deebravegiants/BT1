# [H] Private files publicly accessible with Cloud Storage providers

## Summary
Severity: High
Advisory: GHSA-vrf2-xghr-j52v
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-vrf2-xghr-j52v
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=0 <6.4.1.1
- Packagist: `shopware/core` — affected >=0 <6.4.1.1

## Details
### Impact

Private files publicly accessible with Cloud Storage providers when the hashed URL is known

### Patches

We recommend first changing your configuration to set the correct visibility according to the documentation. The visibility must be at the same level as `type`.

When the Storage is saved on Amazon AWS we recommending disabling public access to the bucket containing the private files: https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html

Otherwise, update to Shopware 6.4.1.1 or install or update the Security plugin (https://store.shopware.com/en/detail/index/sArticle/518463/number/Swag136939272659) and run the command `./bin/console s3:set-visibility` to correct your cloud file visibilities

## References
- https://github.com/shopware/platform/security/advisories/GHSA-vrf2-xghr-j52v
- https://github.com/shopware/platform

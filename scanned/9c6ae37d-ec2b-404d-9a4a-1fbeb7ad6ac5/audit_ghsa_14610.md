# [M] ezsystems/ezplatform-http-cache affected by Breach with Varnish VCL

## Summary
Severity: Medium
Advisory: GHSA-mgfg-7533-7jf6
Ecosystem: Packagist
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-mgfg-7533-7jf6
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-http-cache` — affected >=0 <2.3.16

## Details
### Impact
This is not a vulnerability in the code per se, but included Varnish VCL templates enable compression of API and JSON messages. This is a potential case of the BREACH vulnerability, which affects HTTP compression, where secrets can be extracted through carefully crafted requests. The fix disables compression in these templates. Please make sure to make the same change in your configuration files, see the release notes for specific instructions. Please check your web server configuration as well.

### Patches
- See "Patched versions".
- https://github.com/ezsystems/ezplatform-http-cache/commit/ca8a5cf69b2c14fbec90412aeeef5c755c51457b

### Workarounds
Make sure HTTP compression is disabled for REST API requests and other communication that might contain secrets.

### References
- Advisory: https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- Release notes: https://doc.ibexa.co/en/latest/update_and_migration/from_3.3/update_from_3.3/#v3341
- https://github.com/ibexa/post-install/security/advisories/GHSA-4h8f-c635-25p7
- https://github.com/ibexa/http-cache/security/advisories/GHSA-fh7v-q458-7vmw
- https://www.breachattack.com/

## References
- https://github.com/ezsystems/ezplatform-http-cache/security/advisories/GHSA-mgfg-7533-7jf6
- https://github.com/ibexa/http-cache/security/advisories/GHSA-fh7v-q458-7vmw
- https://github.com/ibexa/post-install/security/advisories/GHSA-4h8f-c635-25p7
- https://github.com/ezsystems/ezplatform-http-cache/commit/ca8a5cf69b2c14fbec90412aeeef5c755c51457b
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- https://doc.ibexa.co/en/latest/update_and_migration/from_3.3/update_from_3.3/#v3341
- https://github.com/ezsystems/ezplatform-http-cache
- https://www.breachattack.com

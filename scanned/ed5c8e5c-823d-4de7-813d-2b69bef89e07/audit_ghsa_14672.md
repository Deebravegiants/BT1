# [M] ibexa/post-install affected by Breach with Varnish VCL

## Summary
Severity: Medium
Advisory: GHSA-4h8f-c635-25p7
Ecosystem: Packagist
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-4h8f-c635-25p7
Type: github-advisory

## Affected
- Packagist: `ibexa/post-install` — affected >=1.0.0 <1.0.16
- Packagist: `ibexa/post-install` — affected >=4.6.0 <4.6.14

## Details
### Impact
This is not a vulnerability in the code per se, but included platform.sh Varnish VCL templates and Apache/Nginx vhost templates enable compression of API and JSON messages. This is a potential case of the BREACH vulnerability, which affects HTTP compression, where secrets can be extracted through carefully crafted requests. The fix disables compression in these templates. Please make sure to make the same change in your configuration files, see the release notes for specific instructions.

### Patches
- See "Patched versions".
- v1.0: https://github.com/ibexa/post-install/commit/d91cc02623dd3263a99a94ace133c95e48909e5d
- v4.6: https://github.com/ibexa/post-install/commit/ae7c3c2081a862c75b90828f08bd74436ceb8fe8

### Workarounds
Make sure HTTP compression is disabled for REST API requests and other communication that might contain secrets.

### References
- Advisory: https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- Release notes v3.3: https://doc.ibexa.co/en/latest/update_and_migration/from_3.3/update_from_3.3/#v3341
- Release notes v4.6: https://doc.ibexa.co/en/latest/update_and_migration/from_4.6/update_from_4.6/#v4614
- https://github.com/ezsystems/ezplatform-http-cache/security/advisories/GHSA-mgfg-7533-7jf6
- https://github.com/ibexa/http-cache/security/advisories/GHSA-fh7v-q458-7vmw
- https://www.breachattack.com/

## References
- https://github.com/ezsystems/ezplatform-http-cache/security/advisories/GHSA-mgfg-7533-7jf6
- https://github.com/ibexa/http-cache/security/advisories/GHSA-fh7v-q458-7vmw
- https://github.com/ibexa/post-install/security/advisories/GHSA-4h8f-c635-25p7
- https://github.com/ibexa/post-install/commit/d91cc02623dd3263a99a94ace133c95e48909e5d
- https://developers.ibexa.co/security-advisories/ibexa-sa-2024-006-vulnerabilities-in-content-name-pattern-commerce-shop-and-varnish-vhost-templates
- https://doc.ibexa.co/en/latest/update_and_migration/from_3.3/update_from_3.3/#v3341
- https://doc.ibexa.co/en/latest/update_and_migration/from_4.6/update_from_4.6/#v4614
- https://github.com/ibexa/post-install
- https://www.breachattack.com

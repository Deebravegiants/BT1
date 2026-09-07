# [M] Silverstripe uses TinyMCE which allows svg files linked in object tags

## Summary
Severity: Medium
Advisory: GHSA-52cw-pvq9-9m5v
CWE: CWE-1395, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-52cw-pvq9-9m5v
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <5.2.16

## Details
### Impact
TinyMCE v6 has a configuration value `convert_unsafe_embeds` set to `false` which allows svg files containing javascript to be used in `<object>` or `<embed>` tags, which can be used as a vector for XSS attacks.

Note that `<embed>` tags are not allowed by default.

After patching the default value of `convert_unsafe_embeds` will be set to `true`. This means that `<object>` tags will be converted to iframes instead the next time the page is saved, which may break any pages that rely upon previously saved `<object>` tags. Developers can override this configuration if desired to revert to the original behaviour.

We reviewed the potential impact of this vulnerability within the context of Silverstripe CMS. We concluded this is a medium impact vulnerability given how TinyMCE is used by Silverstripe CMS.

### References:
- https://www.silverstripe.org/download/security-releases/ss-2024-001
- https://github.com/advisories/GHSA-5359-pvf2-pw78

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-52cw-pvq9-9m5v
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/SS-2024-001.yaml
- https://github.com/advisories/GHSA-5359-pvf2-pw78
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/ss-2024-001

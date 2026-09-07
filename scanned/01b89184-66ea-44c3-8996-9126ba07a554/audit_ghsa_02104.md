# [M] Users can edit the tags of any discussion

## Summary
Severity: Medium
Advisory: GHSA-32wx-4gxx-h48f
CWE: CWE-639
Ecosystem: Packagist
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-32wx-4gxx-h48f
Type: github-advisory

## Affected
- Packagist: `flarum/tags` — affected >=0 <0.1.0-beta.13.2

## Details
This advisory concerns a vulnerability which was patched and publicly released on October 5, 2020.

### Impact
This vulnerability allowed any registered user to edit the tags of any discussion for which they have READ access using the REST API.

Users were able to remove any existing tag, and add any tag in which they are allowed to create discussions. The chosen tags still had to match the configured Tags minimums and maximums.

By moving the discussion to new tags, users were able to go around permissions applied to restricted tags. Depending on the setup, this can include publicly exposing content that was only visible to certain groups, or gain the ability to interact with content where such interaction was limited.

The full impact varies depending on the configuration of permissions and restricted tags, and which community extensions are being used. All tag-scoped permissions offered by extensions are impacted by this ability to go around them.

Forums that don't use restricted tags and don't use any extension that relies on tags for access control should not see any security impact. An update is still required to stop users from being able to change any discussion's tags.

Forums that don't use the Tags extension are unaffected.

### Patches
The fix will be available in version v0.1.0-beta.14 with Flarum beta 14. The fix has already been back-ported to Flarum beta 13 as version v0.1.0-beta.13.2 of the Tags extension.

### Workarounds
Version v0.1.0-beta.13.2 of the Tags extension allows existing Flarum beta 13 forums to fix the issue without the need to update to beta 14.

Forums that have not yet updated to Flarum beta 13 are encouraged to update as soon as possible.

### References

- [Release announcement](https://discuss.flarum.org/d/25059-security-update-to-flarum-tags-010-beta132)
- [GitHub issue](https://github.com/flarum/core/issues/2355)

### For more information
If you have any questions or comments about this advisory, please start a new discussion on our [support forum](https://discuss.flarum.org/t/support).

If you discover a security vulnerability within Flarum, please send an e-mail to [security@flarum.org](mailto:security@flarum.org). All security vulnerabilities will be promptly addressed. More details can be found in our [security policy](https://github.com/flarum/core/security/policy).

## References
- https://github.com/flarum/tags/security/advisories/GHSA-32wx-4gxx-h48f
- https://github.com/flarum/core/issues/2355
- https://github.com/flarum/tags/commit/c8fcd000857493f1e4cc00b6f2771ce388b93e9d
- https://discuss.flarum.org/d/25059-security-update-to-flarum-tags-010-beta132
- https://packagist.org/packages/flarum/tags

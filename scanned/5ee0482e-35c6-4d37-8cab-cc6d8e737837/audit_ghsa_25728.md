# [H] Execution with Unnecessary Privileges in arc-electron

## Summary
Severity: High
Advisory: GHSA-v3wr-67px-44xg
Ecosystem: npm
Published: 2022-03-03
Source: https://github.com/advisories/GHSA-v3wr-67px-44xg
Type: github-advisory

## Affected
- npm: `@advanced-rest-client/base` — affected >=0 <0.1.10

## Details
### Impact

When the end-user click on the response header that contains a link the target will be opened in ARC new window. This window will have the default preload script loaded which allows the scripts embedded in the link target to execute any logic that ARC has access to from the renderer process, which includes file system access, data store access (which may contain sensitive information), and some additional processes that only ARC should have access to.

### Patches

This is patched in version 17.0.9.

### Workarounds

Do not click onto any link in the response headers view.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [advanced-rest-client/arc-electron](https://github.com/advanced-rest-client/arc-electron)
* Email us at [Salesforce Security](mailto:security@salesforce.com)

## References
- https://github.com/advanced-rest-client/arc-electron/security/advisories/GHSA-v3wr-67px-44xg
- https://github.com/advanced-rest-client/arc-electron

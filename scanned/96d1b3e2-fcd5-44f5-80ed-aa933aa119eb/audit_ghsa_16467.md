# [M] eZ Platform Admin UI is vulnerable to Cross-site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-w9p3-26fx-5mp3
CWE: CWE-79
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-w9p3-26fx-5mp3
Type: github-advisory

## Affected
- Packagist: `ezsystems/platform-ui-assets-bundle` — affected >=4.2.0 <4.2.3

## Details
There is an XSS vulnerability in CKEditor, which is used by AlloyEditor, which is used in eZ Platform Admin UI. Scripts can be injected through specially crafted "protected" comments. We are not sure it is exploitable in eZ Platform, but recommend installing it to be on the safe side. It is fixed in CKEditor v4.14, AlloyEditor v2.11.9. It is distributed via Composer, for:
```
eZ Platform v1.13.x: ezsystems/PlatformUIAssetsBundle v4.2.3 (included from ezsystems/PlatformUIBundle v1.13.x)

eZ Platform v2.5.13: ezsystems/ezplatform-admin-ui-assets v4.2.1

eZ Platform v3.0.*: ezsystems/ezplatform-admin-ui-assets v5.0.1

eZ Platform v3.1.2: ezsystems/ezplatform-admin-ui-assets v5.1.1
```

Drafts that are sent to trash become visible in the Review Queue, even for users that were not able to see them before this action. It's not possible to preview them, but their title and review history is displayed. This affects Enterprise Edition only, of which ezplatform-workflow is a part. This security update is distributed via Composer, for
```
eZ Platform EE v2.5.13: ezsystems/ezplatform-workflow v1.1.9

eZ Platform EE v3.1.2: ezsystems/ezplatform-workflow v2.1.1
```

## References
- https://ezplatform.com/security-advisories/ezsa-2020-005-editor-xss-and-trashed-drafts-in-review-queue
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/platform-ui-assets-bundle/2020-08-07-1.yaml
- https://github.com/ezsystems/PlatformUIAssetsBundle

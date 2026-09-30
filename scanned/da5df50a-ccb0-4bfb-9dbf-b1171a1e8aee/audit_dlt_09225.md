# [?] doc: document security fix policy

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2021-03-18
Source: https://github.com/ipfs/kubo/commit/c3b9a3f63872536c1df38df1663c4dd0dc4c99a7
Type: security-commit

## Details
doc: document security fix policy

1. All releases may contain unannounced security fixes.
2. By default, security fixes will not be backported.

## Patch
### docs/RELEASE_ISSUE_TEMPLATE.md
```diff
@@ -4,6 +4,8 @@
 
 We're happy to announce go-ipfs X.Y.Z, bla bla...
 
+As usual, this release includes important fixes, some of which may be critical for security. Unless the fix addresses a bug being exploited in the wild, the fix will _not_ be called out in the release notes. Please make sure to update ASAP. See our [release process](https://github.com/ipfs/go-ipfs/tree/master/docs/releases.md#security-fix-policy) for details.
+
 ## 🗺 What's left for release
 
 <List of items with PRs and/or Issues to be considered for this release>
```

### docs/releases.md
```diff
@@ -83,6 +83,14 @@ Patch releases will usually follow a compressed release cycle and should take 2-
 
 Some patch releases, especially ones fixing one or more complex bugs, may undergo the full release process.
 
+## Security Fix Policy
+
+Any release may contain security fixes. Unless the fix addresses a bug being exploited in the wild, the fix will _not_ be called out in the release notes. Please make sure to update ASAP.
+
+By policy, the team will usually wait until about 2 weeks after the final release to announce any fixed security issues. However, depending on the impact and ease of discovery of the issue, the team may wait more or less time. It is important to always update to the latest version ASAP and file issues if you're unable to update for some reason.
+
+Finally, unless a security issue is actively being exploited or a significant number of users are unable to update to the latest version (e.g., due to a difficult migration, breaking changes, etc.), security fixes will _not_ be backported to previous releases.
+
 ## Performing a Release
 
 The release is managed by the `Lead Maintainer` for `go-ipfs`. It starts with the opening of an issue containing the content available on the [RELEASE_ISSUE_TEMPLATE](./RELEASE_ISSUE_TEMPLATE.md) not more than **48 hours** after the previous release.
```

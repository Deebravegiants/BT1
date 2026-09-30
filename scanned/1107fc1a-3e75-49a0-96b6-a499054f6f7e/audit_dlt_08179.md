# [?] fix(app): Stop panicking at startup when parsing the app version - release blocker (#6888)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-06-09
Source: https://github.com/ZcashFoundation/zebra/commit/a18f47d5f683dbcd6dd0a1e4381621525eb51f41
Type: security-commit

## Details
fix(app): Stop panicking at startup when parsing the app version - release blocker (#6888)

* Fix a startup panic in app_version()

* Fix a potential RPC panic in get_info()

* Fix typo

## Patch
### zebra-rpc/src/methods.rs
```diff
@@ -374,10 +374,10 @@ where
             // remove everything after the `+` character if any
             .split('+')
             .next()
-            .expect("always at least 1 slice")
-            // remove the previously added `v` character at the start since it's not a part of the user agent.
-            .strip_prefix('v')
-            .expect("we are always expecting the `v` prefix");
+            .expect("always at least 1 slice");
+        // Remove the previously added `v` character at the start since it's not a part of the user agent.
+        let release_version = release_version.strip_prefix('v').unwrap_or(release_version);
+
         let user_agent = format!("/Zebra:{release_version}/");
 
         let response = GetInfo {
```

### zebrad/src/application.rs
```diff
@@ -36,45 +36,98 @@ pub static APPLICATION: AppCell<ZebradApp> = AppCell::new();
 ///
 /// For details, see <https://semver.org/>
 pub fn app_version() -> Version {
+    // CARGO_PKG_VERSION is always a valid SemVer 2.0 version.
     const CARGO_PKG_VERSION: &str = env!("CARGO_PKG_VERSION");
-    let vergen_git_describe: Option<&str> = option_env!("VERGEN_GIT_DESCRIBE");
-
-    match vergen_git_describe {
-        // change the git describe format to the semver 2.0 format
-        Some(mut vergen_git_describe) if !vergen_git_describe.is_empty() => {
-            // strip the leading "v", if present
-            if &vergen_git_describe[0..1] == "v" {
-                vergen_git_describe = &vergen_git_describe[1..];
-            }
 
-            // split into tag, commit count, hash
-            let rparts: Vec<_> = vergen_git_describe.rsplitn(3, '-').collect();
-
-            match rparts.as_slice() {
-                // assume it's a cargo package version or a git tag with no hash
-                [_] | [_, _] => vergen_git_describe.parse().unwrap_or_else(|_| {
-                    panic!(
-                        "VERGEN_GIT_DESCRIBE without a hash {vergen_git_describe:?} must be valid semver 2.0"
-                    )
-                }),
-
-                // it's the "git describe" format, which doesn't quite match SemVer 2.0
-                [hash, commit_count, tag] => {
-                    let semver_fix = format!("{tag}+{commit_count}.{hash}");
-                    semver_fix.parse().unwrap_or_else(|_|
-                                                      panic!("Modified VERGEN_GIT_DESCRIBE {vergen_git_describe:?} -> {rparts:?} -> {semver_fix:?} must be valid. Note: CARGO_PKG_VERSION was {CARGO_PKG_VERSION:?}."))
-                }
+    // VERGEN_GIT_DESCRIBE should be in the format:
+    // - v1.0.0-rc.9-6-g319b01bb84
+    // - v1.0.0-6-g319b01bb84
+    // but sometimes it is just a short commit hash. See #6879 for details.
+    //
+    // Currently it is the output of `git describe --tags --dirty --match='v*.*.*'`,
+    // or whatever is specified in zebrad/build.rs.
+    const VERGEN_GIT_DESCRIBE: Option<&str> = option_env!("VERGEN_GIT_DESCRIBE");
+
+    // We're using the same library as cargo uses internally, so this is guaranteed.
+    let fallback_version = CARGO_PKG_VERSION.parse().unwrap_or_else(|error| {
+        panic!(
+            "unexpected invalid CARGO_PKG_VERSION: {error:?} in {CARGO_PKG_VERSION:?}, \
+             should have been checked by cargo"
+        )
+    });
+
+    // The SemVer 2.0 format is:
+    // - 1.0.0-rc.9+6.g319b01bb84
+    // - 1.0.0+6.g319b01bb84
+    //
+    // Or as a pattern:
+    // - version: major`.`minor`.`patch
+    // - optional pre-release: `-`tag[`.`tag ...]
+    // - optional build: `+`tag[`.`tag ...]
+    // change the git describe format to the semver 2.0 format
+    let Some(vergen_git_describe) = VERGEN_GIT_DESCRIBE else {
+        return fallback_version;
+    };
+
+    // Split using "git describe" separators.
+    let mut vergen_git_describe = vergen_git_describe.split('-').peekable();
+
+    // Check the "version core" part.
+    let version = vergen_git_describe.next();
+    let Some(mut version) = version else {
+        return fallback_version;
+    };
+
+    // strip the leading "v", if present.
+    version = version.strip_prefix('v').unwrap_or(version);
+
+    // If the initial version is empty, just a commit hash, or otherwise invalid.
+    if Version::parse(version).is_err() {
+        return fallback_version;
+    }
 
-                _ => unreachable!("split is limited to 3 parts"),
-            }
-        }
-        _ => CARGO_PKG_VERSION.parse().unwrap_or_else(|_| {
-            panic!("CARGO_PKG_VERSION {CARGO_PKG_VERSION:?} must be valid semver 2.0")
-        }),
+    let mut semver = version.to_string();
+
+    // Check if the next part is a pre-release or build part,
+    // but only consume it if it is a pre-release tag.
+    let Some(part) = vergen_git_describe.peek() else {
+        // No pre-release or build.
+        return semver.parse().expect("just checked semver is valid");
+    };
+
+    if part.starts_with(char::is_alphabetic) {
+        // It's a pre-release tag.
+        semver.push('-');
+        semver.push_str(part);
+
+        // Consume the pre-release tag to move on to the build tags, if any.
+        let _ = vergen_git_describe.next();
+    }
+
+    // Check if the next part is a build part.
+    let Some(build) = vergen_git_describe.peek() else {
+        // No build tags.
+        return semver.parse().unwrap_or(fallback_version);
+    };
+
+    if !build.starts_with(char::is_numeric) {
+        // It's not a valid "commit count" build tag from "git describe".
+        return fallback_version;
     }
+
+    // Append the rest of the build parts with the correct `+` and `.` separators.
+    let build_parts: Vec<_> = vergen_git_describe.collect();
+    let build_parts = build_parts.join(".");
+
+    semver.push('+');
+    semver.push_str(&build_parts);
+
+    semver.parse().unwrap_or(fallback_version)
 }
 
 /// The Zebra current release version.
+//
+// TODO: deduplicate this code with release_version in zebra_rpc::get_info()
 pub fn release_version() -> String {
     app_version()
         .to_string()
@@ -89,6 +142,8 @@ pub fn release_version() -> String {
 /// This must be a valid [BIP 14] user agent.
 ///
 /// [BIP 14]: https://github.com/bitcoin/bips/blob/master/bip-0014.mediawiki
+//
+// TODO: deduplicate this code with the user agent in zebra_rpc::get_info()
 pub fn user_agent() -> String {
     let release_version = release_version();
     format!("/Zebra:{release_version}/")
```

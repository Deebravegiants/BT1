# [?] Prevent panic in UserAgent arbitrary

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-06-23
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/eee88730a77556a8486421511fd912f33f36c63f
Type: security-commit

## Details
Prevent panic in UserAgent arbitrary

The current UserAgent arbitrary impl can panic when calling into
UserAgent::new, as it doesn't correctly sanitise the characters and
length of the name. While the decoder doesn't enforce these checks,
unexpected panics in the arbitrary impl are surprising and should be
avoided.

Prevent panics in UserAgent arbitrary impl by sanitising inputs to
UserAgent::new.

## Patch
### p2p/src/message_network.rs
```diff
@@ -778,7 +778,19 @@ impl<'a> Arbitrary<'a> for UserAgentVersion {
 #[cfg(feature = "arbitrary")]
 impl<'a> Arbitrary<'a> for UserAgent {
     fn arbitrary(u: &mut Unstructured<'a>) -> arbitrary::Result<Self> {
-        Ok(Self::new(u.arbitrary::<String>()?, &u.arbitrary()?))
+        let version = UserAgentVersion::arbitrary(u)?;
+
+        let mut name: String = u
+            .arbitrary::<String>()?
+            .chars()
+            .filter(|c| !matches!(c, '/' | '(' | ')' | ':'))
+            .collect();
+
+        let overhead = 3 + version.to_string().chars().count();
+        let max_name = Self::MAX_USER_AGENT_LEN - overhead;
+        name.truncate(max_name);
+
+        Ok(Self::new(name, &version))
     }
 }
 
```

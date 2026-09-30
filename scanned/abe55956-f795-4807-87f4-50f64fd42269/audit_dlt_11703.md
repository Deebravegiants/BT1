# [?] Fix race condition in commit test (#651)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: ordinals/ord
Published: 2022-10-13
Source: https://github.com/ordinals/ord/commit/1ef34e6559dbe3241b03e267b7d5ca85901151c4
Type: security-commit

## Details
Fix race condition in commit test (#651)

## Patch
### src/subcommand/server.rs
```diff
@@ -631,6 +631,10 @@ mod tests {
         thread::spawn(|| server.run(options, index, ord_server_handle).unwrap());
       }
 
+      while index.statistic(crate::index::Statistic::Commits).unwrap() == 0 {
+        thread::sleep(Duration::from_millis(25));
+      }
+
       for i in 0.. {
         match reqwest::blocking::get(&format!("http://127.0.0.1:{port}/status")) {
           Ok(_) => break,
@@ -1399,7 +1403,7 @@ mod tests {
   }
 
   #[test]
-  fn commit_are_tracked() {
+  fn commits_are_tracked() {
     let server = TestServer::new();
 
     assert_eq!(
```

# [?] prevent possible race condition on parallel runs for status_endpoint test

## Summary
Severity: Unknown
Chain: Stacks
Component: stacks-network/stacks-core
Published: 2026-03-20
Source: https://github.com/stacks-network/stacks-core/commit/ca7a721ce1107a62b602b4674a790b2c3bb184e4
Type: security-commit

## Details
prevent possible race condition on parallel runs for status_endpoint test

## Patch
### libsigner/src/tests/mod.rs
```diff
@@ -225,16 +225,12 @@ fn test_status_endpoint() {
     let mut signer = Signer::new(SimpleRunLoop::new(max_events), ev, res_send);
     let endpoint: SocketAddr = "127.0.0.1:31000".parse().unwrap();
 
+    // Spawn the signer first so the HTTP server is listening before the mock client connects
+    let running_signer = signer.spawn(endpoint).unwrap();
+
     // simulate a node that's trying to push data
     let mock_stacks_node = thread::spawn(move || {
-        let mut sock = match TcpStream::connect(endpoint) {
-            Ok(sock) => sock,
-            Err(e) => {
-                eprint!("Error connecting to {endpoint}: {e}");
-                sleep_ms(100);
-                return;
-            }
-        };
+        let mut sock = TcpStream::connect(endpoint).unwrap();
         let req = format!("GET /status HTTP/1.1\r\nHost: {endpoint}\r\nConnection: close\r\n\r\n");
 
         sock.write_all(req.as_bytes()).unwrap();
@@ -245,8 +241,6 @@ fn test_status_endpoint() {
         assert_eq!(expected_status_res, &res_str[..expected_status_res.len()]);
         sock.flush().unwrap();
     });
-
-    let running_signer = signer.spawn(endpoint).unwrap();
     sleep_ms(3000);
     let accepted_events = running_signer.stop().unwrap();
 
```

# [?] Fixes #1017 — unbounded Stratum input buffer allowing remote memory exhaustion (#1023)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-05-29
Source: https://github.com/kaspanet/rusty-kaspa/commit/3cef6adaf2c79cfa34704070a49fe10d712b5729
Type: security-commit

## Details
Fixes #1017 — unbounded Stratum input buffer allowing remote memory exhaustion (#1023)

In spawn_client_listener, each TCP connection accumulated incoming bytes in line_buffer until a \n was received. The buffer had no size limit. A client could send data continuously without a newline (staying within the 5-second per-read timeout) and grow line_buffer without bound for as long as the connection stayed open.

This occurred before JSON-RPC parsing and before miner authorization, so any client reaching the Stratum port (default :5555 / 0.0.0.0:5555) could trigger it.

Fix
Introduced MAX_STRATUM_LINE_BYTES (64 KiB) as the maximum size for an incomplete Stratum line awaiting \n.
Added append_line_data() to check the limit before appending; on rejection the buffer is left unchanged.
In the read loop, if a chunk would exceed the cap, the connection is logged and closed immediately.
Exported both symbols from the crate for testability.
64 KiB is well above legitimate Stratum JSON-RPC messages (typically under 1 KiB) while bounding memory per connection.

Tests
Added five unit tests in bridge/src/tests.rs:

Accepts normal messages under the limit
Accepts incremental chunks up to the limit
Rejects append when the buffer is already at capacity
Rejects a single chunk larger than the limit
Accepts data exactly at the limit, then rejects one byte more

## Patch
### bridge/src/stratum_listener.rs
```diff
@@ -11,6 +11,21 @@ use tokio::sync::mpsc;
 use tokio::sync::watch;
 use tracing::{debug, error, info, warn};
 
+/// Maximum permitted size (in bytes) for an incomplete Stratum line awaiting `\n`.
+/// Legitimate JSON-RPC Stratum messages are well below this; the cap prevents unbounded
+/// memory growth when a client sends data without a newline.
+pub const MAX_STRATUM_LINE_BYTES: usize = 64 * 1024;
+
+/// Append received data to the line buffer. Returns `false` if the append would exceed
+/// [`MAX_STRATUM_LINE_BYTES`], leaving the buffer unchanged.
+pub fn append_line_data(line_buffer: &mut String, data: &str) -> bool {
+    if line_buffer.len().saturating_add(data.len()) > MAX_STRATUM_LINE_BYTES {
+        return false;
+    }
+    line_buffer.push_str(data);
+    true
+}
+
 /// Event handler function type
 pub type EventHandler = Arc<
     dyn Fn(
@@ -467,7 +482,15 @@ impl StratumListener {
                         first_message = false;
                     }
 
-                    line_buffer.push_str(&String::from_utf8_lossy(&data));
+                    let chunk = String::from_utf8_lossy(&data);
+                    if !append_line_data(&mut line_buffer, &chunk) {
+                        warn!(
+                            "[CONNECTION] Client {}:{} exceeded maximum Stratum line size ({} bytes), disconnecting",
+                            ctx.remote_addr, ctx.remote_port, MAX_STRATUM_LINE_BYTES
+                        );
+                        ctx.disconnect();
+                        break;
+                    }
 
                     // Process complete lines
                     while let Some(newline_pos) = line_buffer.find('\n') {
```

### bridge/src/tests.rs
```diff
@@ -481,6 +481,57 @@ fn test_bind_addr_from_port_empty() {
     assert_eq!(bind_addr_from_port("   "), "");
 }
 
+// Stratum line buffer tests (issue #1017 — cap incomplete lines to prevent memory exhaustion)
+#[cfg(test)]
+#[test]
+fn test_append_line_data_accepts_data_under_limit() {
+    use kaspa_stratum_bridge::append_line_data;
+    let mut buf = String::new();
+    assert!(append_line_data(&mut buf, "{\"jsonrpc\":\"2.0\"}\n"));
+    assert_eq!(buf, "{\"jsonrpc\":\"2.0\"}\n");
+}
+
+#[cfg(test)]
+#[test]
+fn test_append_line_data_accepts_incremental_chunks_under_limit() {
+    use kaspa_stratum_bridge::{MAX_STRATUM_LINE_BYTES, append_line_data};
+    let mut buf = String::new();
+    let chunk_size = 1024;
+    let chunks = MAX_STRATUM_LINE_BYTES / chunk_size;
+    for _ in 0..chunks {
+        assert!(append_line_data(&mut buf, &"x".repeat(chunk_size)));
+    }
+    assert_eq!(buf.len(), chunks * chunk_size);
+}
+
+#[cfg(test)]
+#[test]
+fn test_append_line_data_rejects_when_limit_exceeded() {
+    use kaspa_stratum_bridge::{MAX_STRATUM_LINE_BYTES, append_line_data};
+    let mut buf = "x".repeat(MAX_STRATUM_LINE_BYTES);
+    assert!(!append_line_data(&mut buf, "y"));
+    assert_eq!(buf.len(), MAX_STRATUM_LINE_BYTES);
+}
+
+#[cfg(test)]
+#[test]
+fn test_append_line_data_rejects_single_oversized_chunk() {
+    use kaspa_stratum_bridge::{MAX_STRATUM_LINE_BYTES, append_line_data};
+    let mut buf = String::new();
+    assert!(!append_line_data(&mut buf, &"x".repeat(MAX_STRATUM_LINE_BYTES + 1)));
+    assert!(buf.is_empty());
+}
+
+#[cfg(test)]
+#[test]
+fn test_append_line_data_accepts_exactly_at_limit() {
+    use kaspa_stratum_bridge::{MAX_STRATUM_LINE_BYTES, append_line_data};
+    let mut buf = String::new();
+    assert!(append_line_data(&mut buf, &"x".repeat(MAX_STRATUM_LINE_BYTES)));
+    assert_eq!(buf.len(), MAX_STRATUM_LINE_BYTES);
+    assert!(!append_line_data(&mut buf, "y"));
+}
+
 // JSON-RPC event tests
 #[cfg(test)]
 #[test]
```

# [?] graph: fix backoff overflow

## Summary
Severity: Unknown
Chain: The Graph
Component: graphprotocol/graph-node
Published: 2023-03-06
Source: https://github.com/graphprotocol/graph-node/commit/f8d014374d29b8b4c4db0bea186c44ced633e792
Type: security-commit

## Details
graph: fix backoff overflow

## Patch
### graph/src/util/backoff.rs
```diff
@@ -33,7 +33,7 @@ impl ExponentialBackoff {
     }
 
     pub fn delay(&self) -> Duration {
-        let mut delay = self.base.saturating_mul(1 << self.attempt);
+        let mut delay = self.base.saturating_mul(1u32 << self.attempt.min(31));
         if delay > self.ceiling {
             delay = self.ceiling;
         }
@@ -50,3 +50,71 @@ impl ExponentialBackoff {
         self.attempt = 0;
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use std::time::Instant;
+
+    #[test]
+    fn test_delay() {
+        let mut backoff =
+            ExponentialBackoff::new(Duration::from_millis(500), Duration::from_secs(5));
+
+        // First delay should be base (0.5s)
+        assert_eq!(backoff.next_attempt(), Duration::from_millis(500));
+
+        // Second delay should be 1s (base * 2^1)
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(1));
+
+        // Third delay should be 2s (base * 2^2)
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(2));
+
+        // Fourth delay should be 4s (base * 2^3)
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(4));
+
+        // Seventh delay should be ceiling (5s)
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(5));
+
+        // Eighth delay should also be ceiling (5s)
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(5));
+    }
+
+    #[test]
+    fn test_overflow_delay() {
+        let mut backoff =
+            ExponentialBackoff::new(Duration::from_millis(500), Duration::from_secs(45));
+
+        // 31st should be ceiling (45s) without overflowing
+        backoff.attempt = 31;
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(45));
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(45));
+
+        backoff.attempt = 123456;
+        assert_eq!(backoff.next_attempt(), Duration::from_secs(45));
+    }
+
+    #[tokio::test]
+    async fn test_sleep_async() {
+        let mut backoff =
+            ExponentialBackoff::new(Duration::from_secs_f32(0.1), Duration::from_secs_f32(0.2));
+
+        let start = Instant::now();
+        backoff.sleep_async().await;
+        let elapsed = start.elapsed();
+
+        assert!(elapsed >= Duration::from_secs_f32(0.1) && elapsed < Duration::from_secs_f32(0.15));
+
+        let start = Instant::now();
+        backoff.sleep_async().await;
+        let elapsed = start.elapsed();
+
+        assert!(elapsed >= Duration::from_secs_f32(0.2) && elapsed < Duration::from_secs_f32(0.25));
+
+        let start = Instant::now();
+        backoff.sleep_async().await;
+        let elapsed = start.elapsed();
+
+        assert!(elapsed >= Duration::from_secs_f32(0.2) && elapsed < Duration::from_secs_f32(0.25));
+    }
+}
```

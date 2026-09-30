# [?] Fix a possible thread stall resulting in processing delay or OS udp buffer overflow. (#1494)

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2018-12-28
Source: https://github.com/nanocurrency/nano-node/commit/34926f8322ca9f9c22f83c065749661da3be9ed9
Type: security-commit

## Details
Fix a possible thread stall resulting in processing delay or OS udp buffer overflow. (#1494)

## Patch
### rai/node/node.cpp
```diff
@@ -3699,7 +3699,7 @@ void rai::udp_buffer::enqueue (rai::udp_data * data_a)
 		std::lock_guard<std::mutex> lock (mutex);
 		full.push_back (data_a);
 	}
-	condition.notify_one ();
+	condition.notify_all ();
 }
 rai::udp_data * rai::udp_buffer::dequeue ()
 {
@@ -3723,7 +3723,7 @@ void rai::udp_buffer::release (rai::udp_data * data_a)
 		std::lock_guard<std::mutex> lock (mutex);
 		free.push_back (data_a);
 	}
-	condition.notify_one ();
+	condition.notify_all ();
 }
 void rai::udp_buffer::stop ()
 {
```

### rai/node/node.hpp
```diff
@@ -256,9 +256,9 @@ class udp_data
 class udp_buffer
 {
 public:
+	// Stats - Statistics
 	// Size - Size of each individual buffer
 	// Count - Number of buffers to allocate
-	// Stats - Statistics
 	udp_buffer (rai::stat & stats, size_t, size_t);
 	// Return a buffer where UDP data can be put
 	// Method will attempt to return the first free buffer
```

# [?] Fixing thread sanitizer reported data race condition.

## Summary
Severity: Unknown
Chain: Nano
Component: nanocurrency/nano-node
Published: 2017-08-22
Source: https://github.com/nanocurrency/nano-node/commit/f69540c9e8b817c7ab003587b90eef4163e907f5
Type: security-commit

## Details
Fixing thread sanitizer reported data race condition.

## Patch
### rai/node/bootstrap.cpp
```diff
@@ -1040,6 +1040,7 @@ void rai::bootstrap_initiator::add_observer (std::function <void (bool)> const &
 
 bool rai::bootstrap_initiator::in_progress ()
 {
+	std::lock_guard <std::mutex> lock (mutex);
 	return attempt != nullptr;
 }
 
```

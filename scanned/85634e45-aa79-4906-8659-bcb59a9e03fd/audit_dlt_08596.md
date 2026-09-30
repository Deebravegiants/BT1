# [?] Fix short_read test race/deadlock

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2016-02-09
Source: https://github.com/XRPLF/rippled/commit/9f5b58c8ab841e05f372394ca2f69fd13af11e02
Type: security-commit

## Details
Fix short_read test race/deadlock

## Patch
### src/ripple/overlay/tests/short_read.test.cpp
```diff
@@ -140,13 +140,25 @@ class short_read_test : public beast::unit_test::suite
         void
         close()
         {
-            std::unique_lock<std::mutex> lock(mutex_);
-            if (closed_)
-                return;
-            closed_ = true;
-            for(auto& c : list_)
-                if(auto p = c.second.lock())
-                    p->close();
+            std::vector<std::shared_ptr<Child>> v;
+            {
+                std::unique_lock<std::mutex> lock(mutex_);
+                v.reserve(list_.size());
+                if (closed_)
+                    return;
+                closed_ = true;
+                for(auto const& c : list_)
+                {
+                    if(auto p = c.second.lock())
+                    {
+                        p->close();
+                        // Must destroy shared_ptr outside the
+                        // lock otherwise deadlock from the
+                        // managed object's destructor.
+                        v.emplace_back(std::move(p));
+                    }
+                }
+            }
         }
 
         void
```

# [?] Fix potential deadlock in Validator sites:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2021-08-06
Source: https://github.com/XRPLF/rippled/commit/b8552abcea9ab693f419219fea91d80b492ca99a
Type: security-commit

## Details
Fix potential deadlock in Validator sites:

There are two mutexes in ValidatorSite: `site_mutex_` and `state_mutex_`. Some
function end up locking both mutexes. However, depending on the call, the
mutexes could be locked in different orders, resulting in deadlocks.

If both mutexes are locked, this patch always locks the `sites_mutex_` first.

## Patch
### src/ripple/app/misc/ValidatorSite.h
```diff
@@ -117,6 +117,8 @@ class ValidatorSite
     Application& app_;
     beast::Journal const j_;
 
+    // If both mutex are to be locked at the same time, `sites_mutex_` must be
+    // locked before `state_mutex_` or we may deadlock.
     std::mutex mutable sites_mutex_;
     std::mutex mutable state_mutex_;
 
@@ -201,9 +203,11 @@ class ValidatorSite
         std::lock_guard<std::mutex> const&);
 
     /// Queue next site to be fetched
-    /// lock over state_mutex_ required
+    /// lock over site_mutex_ and state_mutex_ required
     void
-    setTimer(std::lock_guard<std::mutex> const&);
+    setTimer(
+        std::lock_guard<std::mutex> const&,
+        std::lock_guard<std::mutex> const&);
 
     /// request took too long
     void
```

### src/ripple/app/misc/impl/ValidatorSite.cpp
```diff
@@ -167,9 +167,10 @@ ValidatorSite::load(
 void
 ValidatorSite::start()
 {
-    std::lock_guard lock{state_mutex_};
+    std::lock_guard l0{sites_mutex_};
+    std::lock_guard l1{state_mutex_};
     if (timer_.expires_at() == clock_type::time_point{})
-        setTimer(lock);
+        setTimer(l0, l1);
 }
 
 void
@@ -206,10 +207,10 @@ ValidatorSite::stop()
 }
 
 void
-ValidatorSite::setTimer(std::lock_guard<std::mutex> const& state_lock)
+ValidatorSite::setTimer(
+    std::lock_guard<std::mutex> const& site_lock,
+    std::lock_guard<std::mutex> const& state_lock)
 {
-    std::lock_guard lock{sites_mutex_};
-
     auto next = std::min_element(
         sites_.begin(), sites_.end(), [](Site const& a, Site const& b) {
             return a.nextRefresh < b.nextRefresh;
@@ -531,8 +532,8 @@ ValidatorSite::onSiteFetch(
     detail::response_type&& res,
     std::size_t siteIdx)
 {
+    std::lock_guard lock_sites{sites_mutex_};
     {
-        std::lock_guard lock_sites{sites_mutex_};
         if (endpoint != endpoint_type{})
             sites_[siteIdx].lastRequestEndpoint = endpoint;
         JLOG(j_.debug()) << "Got completion for "
@@ -606,7 +607,7 @@ ValidatorSite::onSiteFetch(
     std::lock_guard lock_state{state_mutex_};
     fetching_ = false;
     if (!stopping_)
-        setTimer(lock_state);
+        setTimer(lock_sites, lock_state);
     cv_.notify_all();
 }
 
@@ -616,8 +617,8 @@ ValidatorSite::onTextFetch(
     std::string const& res,
     std::size_t siteIdx)
 {
+    std::lock_guard lock_sites{sites_mutex_};
     {
-        std::lock_guard lock_sites{sites_mutex_};
         try
         {
             if (ec)
@@ -643,7 +644,7 @@ ValidatorSite::onTextFetch(
     std::lock_guard lock_state{state_mutex_};
     fetching_ = false;
     if (!stopping_)
-        setTimer(lock_state);
+        setTimer(lock_sites, lock_state);
     cv_.notify_all();
 }
 
```

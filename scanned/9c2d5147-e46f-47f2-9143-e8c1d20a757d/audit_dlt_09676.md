# [?] GH-1815 Avoid deadlock on app_thread

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2023-10-24
Source: https://github.com/AntelopeIO/leap/commit/a4e9df1e4c687d17919bf37694be35c5c1a0e595
Type: security-commit

## Details
GH-1815 Avoid deadlock on app_thread

## Patch
### tests/test_read_only_trx.cpp
```diff
@@ -117,10 +117,6 @@ void test_trxs_common(std::vector<const char*>& specific_args, bool test_disable
             } FC_LOG_AND_DROP()
             BOOST_CHECK(!"app threw exception see logged error");
          } );
-         fc::scoped_exit<std::function<void()>> on_except = [&](){
-            if (app_thread.joinable())
-               app_thread.join();
-         };
 
          auto[prod_plug, chain_plug] = plugin_fut.get();
 
@@ -168,6 +164,7 @@ void test_trxs_common(std::vector<const char*>& specific_args, bool test_disable
          }
 
          app->quit();
+         app_thread.join();
       }
 
       BOOST_CHECK_EQUAL( trace_with_except, 0u ); // should not have any traces with except in it
```

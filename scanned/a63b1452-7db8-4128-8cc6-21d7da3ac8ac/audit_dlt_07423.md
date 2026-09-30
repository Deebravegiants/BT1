# [?] Fixed a rare crash bug when process runs out of file descriptors

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2024-04-22
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/9cdabd25c642c79bb1857b6fe64696b846e873e4
Type: security-commit

## Details
Fixed a rare crash bug when process runs out of file descriptors

Rarely, it would be possible for the process to run out of file
descriptors, in which case ThreadDumper would crash the process
due to unchecked FILE * returned from fopen().

This has been addressed by checking the results of std::fopen() and not
proceeding if the returned FILE * is nullptr.

## Patch
### src/seeder/main.cpp
```diff
@@ -350,6 +350,10 @@ bool StatCompare(const CAddrReport &a, const CAddrReport &b) noexcept {
 }
 
 extern "C" void *ThreadDumper(void *) {
+    auto PrintCantOpenMsg = [](const char *fname) {
+        auto * const errstr = std::strerror(errno);
+        std::fprintf(stderr, "WARNING: Unable to open file '%s': %s\n", fname, errstr);
+    };
     int count = 0;
     do {
         // First 100s, than 200s, 400s, 800s, 1600s, and then 3200s forever
@@ -373,8 +377,17 @@ extern "C" void *ThreadDumper(void *) {
                     std::fprintf(stderr, "WARNING: Unable to save dnsseed.dat, caught exception (%s): %s\n",
                                  typeid(e).name(), e.what());
                 }
+            } else {
+                // This may happen if we run out of file descriptors
+                PrintCantOpenMsg("dnsseed.dat.new");
+                continue;
             }
             FILE *d = fsbridge::fopen("dnsseed.dump", "w");
+            if (!d) {
+                // This may happen if we run out of file descriptors
+                PrintCantOpenMsg("dnsseed.dump");
+                continue;
+            }
             std::fprintf(d, "# address                                        good  "
                             "lastSuccess    %%(2h)   %%(8h)   %%(1d)   %%(7d)  "
                             "%%(30d)  blocks      svcs  version\n");
@@ -398,6 +411,11 @@ extern "C" void *ThreadDumper(void *) {
             }
             std::fclose(d);
             FILE *ff = fsbridge::fopen("dnsstats.log", "a");
+            if (!ff) {
+                // This may happen if we run out of file descriptors
+                PrintCantOpenMsg("dnsstats.log");
+                continue;
+            }
             std::fprintf(ff, "%llu %g %g %g %g %g\n",
                          (unsigned long long)(std::time(nullptr)), stat[0], stat[1],
                          stat[2], stat[3], stat[4]);
```

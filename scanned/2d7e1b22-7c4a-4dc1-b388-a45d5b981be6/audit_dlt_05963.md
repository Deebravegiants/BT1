# [?] Fixed a rare crash bug when process runs out of file descriptors

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2024-04-22
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/f1ce09f06394da028a6a1b1e3042a2cdd0aebc05
Type: security-commit

## Details
Fixed a rare crash bug when process runs out of file descriptors

Rarely, it would be possible for the process to run out of file
descriptors, in which case ThreadDumper -> SaveAllToDisk() would crash.

This has been addressed by checking the results of std::fopen() and not
proceeding if the returned FILE * is nullptr.

## Patch
### src/seeder/main.cpp
```diff
@@ -384,6 +384,10 @@ bool StatCompare(const CAddrReport &a, const CAddrReport &b) noexcept {
 }
 
 void SaveAllToDisk() {
+    auto PrintCantOpenMsg = [](const char *fname) {
+        auto * const errstr = std::strerror(errno);
+        std::fprintf(stderr, "WARNING: Unable to open file '%s': %s\n", fname, errstr);
+    };
     std::vector<CAddrReport> v = db.GetAll();
     std::sort(v.begin(), v.end(), StatCompare);
     FILE *f = fsbridge::fopen("dnsseed.dat.new", "w+");
@@ -398,8 +402,17 @@ void SaveAllToDisk() {
             std::fprintf(stderr, "WARNING: Unable to save dnsseed.dat, caught exception (%s): %s\n",
                          typeid(e).name(), e.what());
         }
+    } else {
+        // This may happen if we run out of file descriptors
+        PrintCantOpenMsg("dnsseed.dat.new");
+        return;
     }
     FILE *d = fsbridge::fopen("dnsseed.dump", "w");
+    if (!d) {
+        // This may happen if we run out of file descriptors
+        PrintCantOpenMsg("dnsseed.dump");
+        return;
+    }
     std::fprintf(d, "# address                                        good  "
                     "lastSuccess    %%(2h)   %%(8h)   %%(1d)   %%(7d)  "
                     "%%(30d)  blocks      svcs  version\n");
@@ -423,6 +436,11 @@ void SaveAllToDisk() {
     }
     std::fclose(d);
     FILE *ff = fsbridge::fopen("dnsstats.log", "a");
+    if (!ff) {
+        // This may happen if we run out of file descriptors
+        PrintCantOpenMsg("dnsstats.log");
+        return;
+    }
     std::fprintf(ff, "%llu %g %g %g %g %g\n",
                  (unsigned long long)(std::time(nullptr)), stat[0], stat[1],
                  stat[2], stat[3], stat[4]);
```

# [?] Fix out of bounds in run_jar.cc (#12774)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-02-04
Source: https://github.com/digital-asset/daml/commit/1df6e951628682b3474b165a8b915efc18b78f30
Type: security-commit

## Details
Fix out of bounds in run_jar.cc (#12774)

changelog_begin
changelog_end

## Patch
### compatibility/bazel_tools/run_jar.cc.tpl
```diff
@@ -81,7 +81,9 @@ int main(int argc, char **argv) {
     return exit_code;
 
 #else
-    char**const argv_ = (char**)malloc((argc + 2) * sizeof(char*));
+    // we replace argv[0], 2 extra args for -jar and the path to the jar
+    // and then the terminating NULL so 3 in total.
+    char**const argv_ = (char**)malloc((argc + 3) * sizeof(char*));
     char* javaStr = new char[java.length() + 1];
     std::strcpy(javaStr, java.c_str());
     argv_[0] = javaStr;
```

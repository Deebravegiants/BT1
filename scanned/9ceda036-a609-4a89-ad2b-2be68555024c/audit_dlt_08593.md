# [?] Avoid stack overflow on AppVeyor:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2018-01-23
Source: https://github.com/XRPLF/rippled/commit/6286a9708ea3611a08b507e8a654553e6317b232
Type: security-commit

## Details
Avoid stack overflow on AppVeyor:

o Reduce json_reader max recursion, and
o Use a GCE VM for AppVeyor

## Patch
### appveyor.yml
```diff
@@ -4,7 +4,7 @@ environment:
 
   # We bundle up protoc.exe and only the parts of boost and openssl we need so
   # that it's a small download. We also use appveyor's free cache, avoiding fees
-  # downloading from S3 each time. 
+  # downloading from S3 each time.
   # TODO: script to create this package.
   RIPPLED_DEPS_PATH: rippled_deps17.02
   RIPPLED_DEPS_URL: https://ripple.github.io/Downloads/appveyor/%RIPPLED_DEPS_PATH%.zip
@@ -21,6 +21,11 @@ environment:
   BOOST_ROOT: C:/%RIPPLED_DEPS_PATH%/boost
   OPENSSL_ROOT: C:/%RIPPLED_DEPS_PATH%/openssl
 
+  # We've had trouble with AppVeyor apparently not having a stack as large
+  # as the *nix CI platforms.  AppVeyor support suggested that we try
+  # GCE VMs.  The following line is supposed to enable that VM type.
+  appveyor_build_worker_cloud: gce
+
   matrix:
   # This build works, but our current Appveyor config runs matrix builds
   # sequentially, and the one build is already slow enough.
@@ -127,7 +132,7 @@ test_script:
   - ps: |
         & {
           # Run the rippled unit tests
-          & $exe --unittest --quiet --unittest-log
+          & $exe --unittest --unittest-log
           # https://connect.microsoft.com/PowerShell/feedback/details/751703/option-to-stop-script-if-command-line-exe-fails
           if ($LastExitCode -ne 0) { throw "Unit tests failed" }
         }
```

### src/ripple/json/json_reader.h
```diff
@@ -81,7 +81,7 @@ class Reader
      */
     std::string getFormatedErrorMessages () const;
 
-    static constexpr unsigned nest_limit {1000};
+    static constexpr unsigned nest_limit {25};
 
 private:
     enum TokenType
```

# [?] Fix CLI crash on unexpected arguments by handling CLI::ParseError

## Summary
Severity: Unknown
Chain: Monad
Component: monad-crypto/monad
Published: 2026-03-12
Source: https://github.com/category-labs/monad/commit/6ec1c855b47c6de39364230c4f9762a4b1a77311
Type: security-commit

## Details
Fix CLI crash on unexpected arguments by handling CLI::ParseError

The CLI previously only handled CLI::CallForHelp and CLI::RequiredError.
Other CLI11 parsing errors (such as CLI::ExtrasError) were not caught,
causing std::terminate to be triggered and resulting in a crash with a
stacktrace.

This change catches CLI::ParseError, the base class for CLI11 parsing
errors, ensuring that invalid CLI usage results in a clean error message
and exit instead of a crash.

## Patch
### cmd/monad/main.cpp
```diff
@@ -226,10 +226,7 @@ try {
     try {
         cli.parse(argc, argv);
     }
-    catch (CLI::CallForHelp const &e) {
-        return cli.exit(e);
-    }
-    catch (CLI::RequiredError const &e) {
+    catch (CLI::ParseError const &e) {
         return cli.exit(e);
     }
 
@@ -512,3 +509,11 @@ catch (monad::MonadException const &e) {
     e.print();
     return EXIT_FAILURE;
 }
+catch (std::exception const &e) {
+    LOG_ERROR("Unhandled std::exception: {}", e.what());
+    return EXIT_FAILURE;
+}
+catch (...) {
+    LOG_ERROR("Unhandled unknown exception");
+    return EXIT_FAILURE;
+}
```

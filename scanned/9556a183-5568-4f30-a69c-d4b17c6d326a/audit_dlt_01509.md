# [?] easylogging++: fix potential memory corruption

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2021-02-13
Source: https://github.com/monero-project/monero/commit/8889f490ce8e4fc0e7f7b9c47f8ef46f5a509cf3
Type: security-commit

## Details
easylogging++: fix potential memory corruption

The m_typedConfigurations pointer is copied from one object to the next,
but deleted in the dtor, leading to potential double free. It is also
deleted first thing in the copy ctor, deleting uninitialized memory.

This does not seem to actually happen in practice (those functions do
not get called), but seems safer that way.

Coverity 1446562

## Patch
### external/easylogging++/easylogging++.cc
```diff
@@ -713,9 +713,8 @@ Logger::Logger(const std::string& id, const Configurations& configurations,
 }
 
 Logger::Logger(const Logger& logger) {
-  base::utils::safeDelete(m_typedConfigurations);
   m_id = logger.m_id;
-  m_typedConfigurations = logger.m_typedConfigurations;
+  m_typedConfigurations = logger.m_typedConfigurations ? new base::TypedConfigurations(*logger.m_typedConfigurations) : nullptr;
   m_parentApplicationName = logger.m_parentApplicationName;
   m_isConfigured = logger.m_isConfigured;
   m_configurations = logger.m_configurations;
@@ -727,7 +726,7 @@ Logger& Logger::operator=(const Logger& logger) {
   if (&logger != this) {
     base::utils::safeDelete(m_typedConfigurations);
     m_id = logger.m_id;
-    m_typedConfigurations = logger.m_typedConfigurations;
+    m_typedConfigurations = logger.m_typedConfigurations ? new base::TypedConfigurations(*logger.m_typedConfigurations) : nullptr;
     m_parentApplicationName = logger.m_parentApplicationName;
     m_isConfigured = logger.m_isConfigured;
     m_configurations = logger.m_configurations;
```

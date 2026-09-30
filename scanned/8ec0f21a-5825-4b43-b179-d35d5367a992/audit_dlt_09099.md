# [?] fix(legacy): Improve handling of busy deadline overflow.

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-09-23
Source: https://github.com/trezor/trezor-firmware/commit/adaa63f94b04c7ca185d23ff2f0b476fc3dd7253
Type: security-commit

## Details
fix(legacy): Improve handling of busy deadline overflow.

[no changelog]

## Patch
### legacy/firmware/fsm_msg_common.h
```diff
@@ -75,7 +75,7 @@ bool get_features(Features *resp) {
   resp->has_safety_checks = true;
   resp->safety_checks = config_getSafetyCheckLevel();
   resp->has_busy = true;
-  resp->busy = (system_millis_busy_deadline > timer_ms());
+  resp->busy = trezor_is_busy();
   if (session_isUnlocked()) {
     resp->has_wipe_code_protection = true;
     resp->wipe_code_protection = config_hasWipeCode();
@@ -592,9 +592,9 @@ void fsm_msgGetFirmwareHash(const GetFirmwareHash *msg) {
 
 void fsm_msgSetBusy(const SetBusy *msg) {
   if (msg->has_expiry_ms) {
-    system_millis_busy_deadline = timer_ms() + msg->expiry_ms;
+    trezor_set_busy(msg->expiry_ms);
   } else {
-    system_millis_busy_deadline = 0;
+    trezor_set_busy(0);
   }
   fsm_sendSuccess(NULL);
   layoutHome();
```

### legacy/firmware/layout2.c
```diff
@@ -300,7 +300,7 @@ void layoutProgressSwipe(const char *desc, int permil) {
 }
 
 void layoutScreensaver(void) {
-  if (system_millis_busy_deadline > timer_ms()) {
+  if (trezor_is_busy()) {
     // Busy screen overrides the screensaver.
     layoutBusyscreen();
   } else {
@@ -316,7 +316,7 @@ void layoutHome(void) {
     system_millis_lock_start = timer_ms();
   }
 
-  if (system_millis_busy_deadline > timer_ms()) {
+  if (trezor_is_busy()) {
     layoutBusyscreen();
   } else {
     layoutHomescreen();
```

### legacy/firmware/trezor.c
```diff
@@ -64,7 +64,8 @@ void secp256k1_default_error_callback_fn(const char *str, void *data) {
 uint32_t system_millis_lock_start = 0;
 
 /* Busyscreen timeout */
-uint32_t system_millis_busy_deadline = 0;
+static uint32_t system_millis_busy_start = 0;
+static uint32_t system_millis_busy_length = 0;
 
 void check_lock_screen(void) {
   buttonUpdate();
@@ -117,11 +118,19 @@ void check_lock_screen(void) {
   }
 }
 
+void trezor_set_busy(uint32_t length_ms) {
+  system_millis_busy_start = timer_ms();
+  system_millis_busy_length = length_ms;
+}
+
+bool trezor_is_busy(void) {
+  return timer_ms() - system_millis_busy_start < system_millis_busy_length;
+}
+
 void check_busy_screen(void) {
   // Clear the busy screen once it expires.
-  if (system_millis_busy_deadline != 0 &&
-      system_millis_busy_deadline < timer_ms()) {
-    system_millis_busy_deadline = 0;
+  if (system_millis_busy_length != 0 && !trezor_is_busy()) {
+    system_millis_busy_length = 0;
     layoutHome();
   }
 }
```

### legacy/firmware/trezor.h
```diff
@@ -20,6 +20,7 @@
 #ifndef __TREZOR_H__
 #define __TREZOR_H__
 
+#include <stdbool.h>
 #include <stdint.h>
 #include "version.h"
 
@@ -38,6 +39,7 @@
 extern uint32_t system_millis_lock_start;
 
 /* Busyscreen timeout */
-extern uint32_t system_millis_busy_deadline;
+void trezor_set_busy(uint32_t length_ms);
+bool trezor_is_busy(void);
 
 #endif
```

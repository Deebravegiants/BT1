# [?] fix(core): fix deadlock in systask_kill()

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-08-03
Source: https://github.com/trezor/trezor-firmware/commit/505a9d65346c1e8406ca2b832cc1e9cf77ccb8d1
Type: security-commit

## Details
fix(core): fix deadlock in systask_kill()

[no changelog]

## Patch
### core/embed/sys/task/inc/sys/systask.h
```diff
@@ -360,7 +360,7 @@ systask_id_t systask_id(const systask_t* task);
  * @param task Pointer to the task to terminate, or NULL.
  * @param exit_code Exit code for the task.
  */
-void __attribute__((noreturn)) systask_exit(systask_t* task, int exit_code);
+void systask_exit(systask_t* task, int exit_code);
 
 /**
  * @brief Terminates the task with an error message
@@ -375,9 +375,9 @@ void __attribute__((noreturn)) systask_exit(systask_t* task, int exit_code);
  * @param footer Footer string.
  * @param footer_len Length of the footer.
  */
-void __attribute__((noreturn)) systask_exit_error(
-    systask_t* task, const char* title, size_t title_len, const char* message,
-    size_t message_len, const char* footer, size_t footer_len);
+void systask_exit_error(systask_t* task, const char* title, size_t title_len,
+                        const char* message, size_t message_len,
+                        const char* footer, size_t footer_len);
 
 /**
  * @brief Terminates the task with a fatal error message
@@ -391,11 +391,9 @@ void __attribute__((noreturn)) systask_exit_error(
  * @param file_len Length of the file string.
  * @param line Line number.
  */
-void __attribute__((noreturn)) systask_exit_fatal(systask_t* task,
-                                                  const char* message,
-                                                  size_t message_len,
-                                                  const char* file,
-                                                  size_t file_len, int line);
+void systask_exit_fatal(systask_t* task, const char* message,
+                        size_t message_len, const char* file, size_t file_len,
+                        int line);
 
 /**
  * @brief Prints the post-mortem information about the task to the debug output
```

### core/embed/sys/task/stm32/systask.c
```diff
@@ -340,7 +340,7 @@ uint32_t systask_get_r0(systask_t* task) {
   return stack[STK_FRAME_R0];
 }
 
-static void __attribute__((noreturn)) systask_kill(systask_t* task) {
+static void systask_kill(systask_t* task) {
   systask_scheduler_t* scheduler = &g_systask_scheduler;
 
   task->killed = 1;
@@ -362,10 +362,6 @@ static void __attribute__((noreturn)) systask_kill(systask_t* task) {
     // Switch to the kernel task
     systask_yield_to(&scheduler->kernel_task);
   }
-
-  while (1) {
-    // This point should never be reached
-  }
 }
 
 bool systask_is_alive(const systask_t* task) {
```

### core/embed/sys/task/system.c
```diff
@@ -24,18 +24,31 @@
 
 #ifdef KERNEL_MODE
 
-void system_exit(int exitcode) { systask_exit(NULL, exitcode); }
+void __attribute__((noreturn)) system_exit(int exitcode) {
+  systask_exit(NULL, exitcode);
+  while (1) {
+    // This point should never be reached
+  }
+}
 
-void system_exit_error_ex(const char* title, size_t title_len,
-                          const char* message, size_t message_len,
-                          const char* footer, size_t footer_len) {
+void __attribute__((noreturn)) system_exit_error_ex(
+    const char* title, size_t title_len, const char* message,
+    size_t message_len, const char* footer, size_t footer_len) {
   systask_exit_error(NULL, title, title_len, message, message_len, footer,
                      footer_len);
+  while (1) {
+    // This point should never be reached
+  }
 }
 
-void system_exit_fatal_ex(const char* message, size_t message_len,
-                          const char* file, size_t file_len, int line) {
+void __attribute__((noreturn)) system_exit_fatal_ex(const char* message,
+                                                    size_t message_len,
+                                                    const char* file,
+                                                    size_t file_len, int line) {
   systask_exit_fatal(NULL, message, message_len, file, file_len, line);
+  while (1) {
+    // This point should never be reached
+  }
 }
 
 #endif  // KERNEL_MODE
```

### core/embed/sys/task/unix/systask.c
```diff
@@ -224,7 +224,7 @@ bool systask_push_call(systask_t* task, void* fn, uintptr_t arg1,
   return true;
 }
 
-static void __attribute__((noreturn)) systask_kill(systask_t* task) {
+static void systask_kill(systask_t* task) {
   systask_scheduler_t* scheduler = &g_systask_scheduler;
 
   systask_print_pminfo(task);
@@ -248,10 +248,6 @@ static void __attribute__((noreturn)) systask_kill(systask_t* task) {
     // Switch to the kernel task
     systask_yield_to(&scheduler->kernel_task);
   }
-
-  while (1) {
-    // This point should never be reached
-  }
 }
 
 bool systask_is_alive(const systask_t* task) {
```

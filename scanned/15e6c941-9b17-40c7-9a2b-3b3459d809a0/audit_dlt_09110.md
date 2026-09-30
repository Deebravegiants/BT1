# [?] fix(core): panic on invalid syscall number

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-01-13
Source: https://github.com/trezor/trezor-firmware/commit/f3793fd8c4288e977aa0b8beec7b04ea05074d9d
Type: security-commit

## Details
fix(core): panic on invalid syscall number

[no changelog]

## Patch
### core/embed/sys/syscall/stm32/syscall_dispatch.c
```diff
@@ -674,7 +674,7 @@ __attribute((no_stack_protector)) void syscall_handler(uint32_t *args,
     } break;
 
     default:
-      args[0] = 0xffffffff;
+      system_exit_fatal("Invalid syscall", __FILE__, __LINE__);
       break;
   }
 }
```

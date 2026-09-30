# [?] device_ledger: add paranoid buffer overflow check

## Summary
Severity: Unknown
Chain: Monero
Component: monero-project/monero
Published: 2019-07-03
Source: https://github.com/monero-project/monero/commit/7c894fc7fd1bcccbb9850ad1088c0f0ac006c427
Type: security-commit

## Details
device_ledger: add paranoid buffer overflow check

Coverity 200183

## Patch
### src/device/device_ledger.cpp
```diff
@@ -320,7 +320,9 @@ namespace hw {
     bool device_ledger::reset() {
       reset_buffer();
       int offset = set_command_header_noopt(INS_RESET);
-      memmove(this->buffer_send+offset, MONERO_VERSION, strlen(MONERO_VERSION));
+      const size_t verlen = strlen(MONERO_VERSION);
+      ASSERT_X(offset + verlen <= BUFFER_SEND_SIZE, "MONERO_VERSION is too long")
+      memmove(this->buffer_send+offset, MONERO_VERSION, verlen);
       offset += strlen(MONERO_VERSION);
       this->buffer_send[4] = offset-5;
       this->length_send = offset;
```

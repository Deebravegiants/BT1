# [?] fix(core): fix OOB read in read_vendor_header

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2026-03-26
Source: https://github.com/trezor/trezor-firmware/commit/3b64e4e8910ea491115e6260978b04e90cc7e1bf
Type: security-commit

## Details
fix(core): fix OOB read in read_vendor_header

[no changelog]

## Patch
### core/embed/projects/bootloader/emulator.c
```diff
@@ -75,7 +75,7 @@ bool load_firmware(const char *filename, uint8_t *hash) {
 
   // read vendor and image header
   vendor_header vhdr;
-  if (sectrue != read_vendor_header(buffer, &vhdr)) {
+  if (sectrue != read_vendor_header(buffer, sizeof(buffer), &vhdr)) {
     printf("File '%s' does not contain a valid vendor header.\n", filename);
     return false;
   }
```

### core/embed/projects/bootloader/fw_check.c
```diff
@@ -64,8 +64,8 @@ void fw_check(fw_info_t *fw_info) {
   volatile secbool version_ok = secfalse;
   volatile secbool secmon_valid = secfalse;
 
-  vhdr_present =
-      read_vendor_header((const uint8_t *)FIRMWARE_START, &fw_info->vhdr);
+  vhdr_present = read_vendor_header((const uint8_t *)FIRMWARE_START,
+                                    VENDOR_HEADER_MAX_SIZE, &fw_info->vhdr);
 
   if (sectrue == vhdr_present) {
     vhdr_keys_ok = check_vendor_header_keys(&fw_info->vhdr);
```

### core/embed/projects/bootloader/main.c
```diff
@@ -124,7 +124,8 @@ static secbool is_manufacturing_mode(void) {
 
   vendor_header vhdr;
   memset(&vhdr, 0, sizeof(vhdr));
-  (void)!read_vendor_header((const uint8_t *)FIRMWARE_START, &vhdr);
+  (void)!read_vendor_header((const uint8_t *)FIRMWARE_START,
+                            VENDOR_HEADER_MAX_SIZE, &vhdr);
 
   if ((vhdr.vtrust & VTRUST_ALLOW_PROVISIONING) != VTRUST_ALLOW_PROVISIONING) {
     return secfalse;
@@ -419,7 +420,8 @@ void real_jump_to_firmware(void) {
   const image_header *hdr = NULL;
   vendor_header vhdr = {0};
 
-  ensure(read_vendor_header((const uint8_t *)FIRMWARE_START, &vhdr),
+  ensure(read_vendor_header((const uint8_t *)FIRMWARE_START,
+                            VENDOR_HEADER_MAX_SIZE, &vhdr),
          "Firmware is corrupted");
 
   ensure(check_vendor_header_keys(&vhdr), "Firmware is corrupted");
```

### core/embed/projects/bootloader/workflow/wf_firmware_update.c
```diff
@@ -211,7 +211,8 @@ static upload_status_t process_msg_FirmwareUpload(protob_io_t *iface,
       // first block and headers are not yet parsed
       vendor_header vhdr;
 
-      if (sectrue != read_vendor_header((uint8_t *)chunk_buffer, &vhdr)) {
+      if (sectrue != read_vendor_header((uint8_t *)chunk_buffer,
+                                        IMAGE_CHUNK_SIZE, &vhdr)) {
         send_msg_failure(iface, FailureType_Failure_ProcessError,
                          "Invalid vendor header");
         return UPLOAD_ERR_INVALID_VENDOR_HEADER;
@@ -308,8 +309,9 @@ static upload_status_t process_msg_FirmwareUpload(protob_io_t *iface,
 
       secbool is_new = secfalse;
 
-      if (sectrue !=
-          read_vendor_header((const uint8_t *)FIRMWARE_START, &current_vhdr)) {
+      if (sectrue != read_vendor_header((const uint8_t *)FIRMWARE_START,
+                                        VENDOR_HEADER_MAX_SIZE,
+                                        &current_vhdr)) {
         is_new = sectrue;
       }
 
```

### core/embed/projects/bootloader_ci/main.c
```diff
@@ -200,7 +200,8 @@ int main(void) {
   // detect whether the device contains a valid firmware
   secbool firmware_present = sectrue;
 
-  if (sectrue != read_vendor_header((const uint8_t *)FIRMWARE_START, &vhdr)) {
+  if (sectrue != read_vendor_header((const uint8_t *)FIRMWARE_START,
+                                    VENDOR_HEADER_MAX_SIZE, &vhdr)) {
     firmware_present = secfalse;
   }
 
@@ -243,7 +244,8 @@ int main(void) {
     return 1;
   }
 
-  ensure(read_vendor_header((const uint8_t *)FIRMWARE_START, &vhdr),
+  ensure(read_vendor_header((const uint8_t *)FIRMWARE_START,
+                            VENDOR_HEADER_MAX_SIZE, &vhdr),
          "invalid vendor header");
 
   ensure(check_vendor_header_keys(&vhdr), "invalid vendor header signature");
```

### core/embed/projects/bootloader_ci/messages.c
```diff
@@ -484,7 +484,8 @@ int process_msg_FirmwareUpload(uint8_t iface_num, uint32_t msg_size,
       // first block and headers are not yet parsed
       vendor_header vhdr;
 
-      if (sectrue != read_vendor_header((uint8_t *)chunk_buffer, &vhdr)) {
+      if (sectrue != read_vendor_header((uint8_t *)chunk_buffer,
+                                        IMAGE_CHUNK_SIZE, &vhdr)) {
         MSG_SEND_INIT(Failure);
         MSG_SEND_ASSIGN_VALUE(code, FailureType_Failure_ProcessError);
         MSG_SEND_ASSIGN_STRING(message, "Invalid vendor header");
@@ -536,8 +537,9 @@ int process_msg_FirmwareUpload(uint8_t iface_num, uint32_t msg_size,
 
       secbool is_new = secfalse;
 
-      if (sectrue !=
-          read_vendor_header((const uint8_t *)FIRMWARE_START, &current_vhdr)) {
+      if (sectrue != read_vendor_header((const uint8_t *)FIRMWARE_START,
+                                        VENDOR_HEADER_MAX_SIZE,
+                                        &current_vhdr)) {
         is_new = sectrue;
       }
 
```

### core/embed/sec/fwutils/fwutils.c
```diff
@@ -111,7 +111,8 @@ secbool firmware_get_vendor(char* buff, size_t buff_size) {
 
   memset(buff, 0, buff_size);
 
-  if (data == NULL || sectrue != read_vendor_header(data, &vhdr)) {
+  if (data == NULL ||
+      sectrue != read_vendor_header(data, VENDOR_HEADER_MAX_SIZE, &vhdr)) {
     return secfalse;
   }
 
```

### core/embed/sec/image/image.c
```diff
@@ -263,14 +263,25 @@ secbool check_secmon_contents(const secmon_header_t *const hdr,
 
 #endif  // USE_SECMON_VERIFICATION
 
-secbool __wur read_vendor_header(const uint8_t *const data,
+secbool __wur read_vendor_header(const uint8_t *const data, size_t data_size,
                                  vendor_header *const vhdr) {
+  // Need at least 23 bytes to safely read all fixed-offset fields through
+  // fw_type at offset 22.
+  if (data_size < 23) return secfalse;
+
   memcpy(&vhdr->magic, data, 4);
   if (vhdr->magic != 0x565A5254) return secfalse;  // TRZV
 
   memcpy(&vhdr->hdrlen, data + 4, 4);
   if (vhdr->hdrlen > VENDOR_HEADER_MAX_SIZE) return secfalse;
 
+  // hdrlen must be large enough to hold the IMAGE_SIG_SIZE-byte signature at
+  // its tail; otherwise the offset data + hdrlen - IMAGE_SIG_SIZE underflows.
+  if (vhdr->hdrlen < IMAGE_SIG_SIZE) return secfalse;
+
+  // The full declared header must fit within the provided buffer.
+  if (data_size < vhdr->hdrlen) return secfalse;
+
   memcpy(&vhdr->expiry, data + 8, 4);
   if (vhdr->expiry != 0) return secfalse;
 
@@ -288,6 +299,13 @@ secbool __wur read_vendor_header(const uint8_t *const data,
     return secfalse;
   }
 
+  // The public-key array and the vstr_len byte that follows it must all fit
+  // within the header body (the region before the trailing signature).
+  uint32_t vstr_len_offset = 32 + (uint32_t)vhdr->vsig_n * 32;
+  if (vstr_len_offset >= vhdr->hdrlen - IMAGE_SIG_SIZE) {
+    return secfalse;
+  }
+
   for (int i = 0; i < vhdr->vsig_n; i++) {
     vhdr->vpub[i] = data + 32 + i * 32;
   }
@@ -466,13 +484,20 @@ secbool check_firmware_header(const uint8_t *header, size_t header_size,
                               firmware_header_info_t *info) {
   // parse and check vendor header
   vendor_header vhdr;
-  if (sectrue != read_vendor_header(header, &vhdr)) {
+  if (sectrue != read_vendor_header(header, header_size, &vhdr)) {
     return secfalse;
   }
   if (sectrue != check_vendor_header_keys(&vhdr)) {
     return secfalse;
   }
 
+  // Ensure the image header fits within the provided buffer after the vendor
+  // header.
+  if (header_size < vhdr.hdrlen ||
+      header_size - vhdr.hdrlen < IMAGE_HEADER_SIZE) {
+    return secfalse;
+  }
+
   // parse and check image header
   const image_header *ihdr;
   if ((ihdr = read_image_header(header + vhdr.hdrlen, FIRMWARE_IMAGE_MAGIC,
```

### core/embed/sec/image/inc/sec/image.h
```diff
@@ -163,7 +163,7 @@ secbool __wur check_image_header_sig(const image_header *const hdr,
                                      uint8_t key_m, uint8_t key_n,
                                      const uint8_t *const *keys);
 
-secbool __wur read_vendor_header(const uint8_t *const data,
+secbool __wur read_vendor_header(const uint8_t *const data, size_t data_Size,
                                  vendor_header *const vhdr);
 
 secbool __wur check_vendor_header_model(const vendor_header *const vhdr);
```

### core/embed/sec/storage/stm32u5/storage_salt.c
```diff
@@ -37,7 +37,9 @@ void storage_salt_get(storage_salt_t* salt) {
   memset(salt, 0, sizeof(*salt));
 
   vendor_header vhdr = {0};
-  ensure(read_vendor_header((const uint8_t*)FIRMWARE_START, &vhdr), NULL);
+  ensure(read_vendor_header((const uint8_t*)FIRMWARE_START,
+                            VENDOR_HEADER_MAX_SIZE, &vhdr),
+         NULL);
 
   _Static_assert(SECRET_KEY_STORAGE_SALT_SIZE <= sizeof(salt->bytes));
   secbool retval = secret_key_storage_salt(vhdr.fw_type, salt->bytes);
```

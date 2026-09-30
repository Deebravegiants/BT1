# [?] fix(crypto): Fix side-channel vulnerability in BIP-39 mnemonic processing

## Summary
Severity: Unknown
Chain: Trezor
Component: trezor/trezor-firmware
Published: 2025-11-12
Source: https://github.com/trezor/trezor-firmware/commit/9b1c06205c41811abe7de81d9e50abd22613f0b3
Type: security-commit

## Details
fix(crypto): Fix side-channel vulnerability in BIP-39 mnemonic processing

Fix function `mnemonic_to_bits` to be constant time. Replace binary search over the wordlist with a linear search to ensure the same number of comparisons.
Introduce function `constant_time_memeq` that comapres two parts of memory in costant time.
Remove integrity check in legacy to reduce the number of computations over seed.

(cherry picked from commit 4e6f0dee81b4d9e553d247faa3194b8053b74dcb)

## Patch
### core/.changelog.d/200.security
```diff
@@ -0,0 +1 @@
+Fixed side-channel vulnerability in BIP-39 mnemonic processing.
```

### core/tests/test_trezor.crypto.bip39.py
```diff
@@ -158,6 +158,7 @@ def test_check_ok(self):
             "board flee heavy tunnel powder denial science ski answer betray cargo cat",
             "board blade invite damage undo sun mimic interest slam gaze truly inherit resist great inject rocket museum chief",
             "beyond stage sleep clip because twist token leaf atom beauty genius food business side grid unable middle armed observe pair crouch tonight away coconut",
+            "abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract abstract artefact electric",
         ]
         for m in v:
             self.assertEqual(bip39.check(m), True)
```

### crypto/bip39.c
```diff
@@ -87,78 +87,95 @@ const char *mnemonic_from_data(const uint8_t *data, int len) {
 
 void mnemonic_clear(void) { memzero(mnemo, sizeof(mnemo)); }
 
-int mnemonic_to_bits(const char *mnemonic, uint8_t *bits) {
-  if (!mnemonic) {
+int mnemonic_to_bits(const char *mnemonic_orig, uint8_t *bits) {
+  if (!mnemonic_orig) {
     return 0;
   }
 
-  uint32_t i = 0, n = 0;
+  // Extended buffer to prevent reading out of bounds in `mnemonic_find_word()`
+  // that requires at least BIP39_MAX_WORD_LEN bytes. The extra bytes in
+  // `mnemonic` are not actually needed; however, they make this function more
+  // robust and easier to analyze.
+  char mnemonic[BIP39_MAX_MNEMONIC_LEN + BIP39_MAX_WORD_LEN + 1] = {0};
+  uint8_t result[32 + 1] = {0};
+  int result_bits = 0;
 
-  while (mnemonic[i]) {
-    if (mnemonic[i] == ' ') {
-      n++;
-    }
-    i++;
+  size_t mnemonic_len = strlen(mnemonic_orig);
+  if (mnemonic_len > BIP39_MAX_MNEMONIC_LEN) {
+    goto cleanup;
+  }
+
+  // Copy the mnemonic into a larger buffer and replace spaces with null bytes
+  // to allow comparison with null-terminated dictionary words.
+  uint32_t word_count = 0;
+  for (uint16_t i = 0; i < mnemonic_len; i++) {
+    bool is_space = mnemonic_orig[i] == ' ';
+    int8_t space_mask = (-is_space) & ' ';
+    mnemonic[i] = mnemonic_orig[i] ^ space_mask;  // change ' ' to 0x00
+    word_count += is_space;
   }
-  n++;
+  word_count++;
 
   // check that number of words is valid for BIP-39:
   // (a) between 128 and 256 bits of initial entropy (12 - 24 words)
   // (b) number of bits divisible by 33 (1 checksum bit per 32 input bits)
-  //     - that is, (n * 11) % 33 == 0, so n % 3 == 0
-  if (n < 12 || n > 24 || (n % 3)) {
-    return 0;
+  //     - that is, (word_count * 11) % 33 == 0, so word_count % 3 == 0
+  if (word_count < 12 || word_count > 24 || (word_count % 3)) {
+    goto cleanup;
   }
 
-  char current_word[10] = {0};
-  uint32_t j = 0, ki = 0, bi = 0;
-  uint8_t result[32 + 1] = {0};
-
   memzero(result, sizeof(result));
-  i = 0;
-  while (mnemonic[i]) {
-    j = 0;
-    while (mnemonic[i] != ' ' && mnemonic[i] != 0) {
-      if (j >= sizeof(current_word) - 1) {
-        return 0;
-      }
-      current_word[j] = mnemonic[i];
-      i++;
-      j++;
-    }
-    current_word[j] = 0;
-    if (mnemonic[i] != 0) {
-      i++;
-    }
-    int k = mnemonic_find_word(current_word);
-    if (k < 0) {  // word not found
-      return 0;
+  uint32_t bit_count = 0;
+  uint32_t word_offset = 0;  // index of beginning of current word
+  while (word_offset < mnemonic_len) {
+    found_word found = mnemonic_find_word(&mnemonic[word_offset]);
+    // move to next word (skip the 0x00 separator)
+    word_offset += found.length + 1;
+
+    int index = found.index;
+    if (index < 0) {  // word not found
+      goto cleanup;
     }
-    for (ki = 0; ki < 11; ki++) {
-      if (k & (1 << (10 - ki))) {
-        result[bi / 8] |= 1 << (7 - (bi % 8));
-      }
-      bi++;
+    for (uint32_t bit_in_index = 0; bit_in_index < BIP39_BITS_PER_WORD;
+         bit_in_index++) {
+      // 1. Extract the secret bit (result is 0 or 1)
+      uint32_t secret_bit =
+          (index >> (BIP39_BITS_PER_WORD - 1 - bit_in_index)) & 1;
+
+      // 2. Create a mask based on the secret bit value
+      // If secret_bit is 1, mask becomes -1 (0xFFFFFFFF)
+      // If secret_bit is 0, mask becomes  0 (0x00000000)
+      int32_t mask = -secret_bit;
+
+      // 3. Apply the mask to the value and perform the OR operation
+      // This operation is only effective if the mask is all 1s.
+      result[bit_count / 8] |= ((1 << (7 - (bit_count % 8))) & mask);
+
+      bit_count++;
     }
   }
-  if (bi != n * 11) {
-    return 0;
+  if (bit_count != word_count * BIP39_BITS_PER_WORD) {
+    goto cleanup;
   }
+
   memcpy(bits, result, sizeof(result));
-  memzero(result, sizeof(result));
+  result_bits = bit_count;
 
-  // returns amount of entropy + checksum BITS
-  return n * 11;
+cleanup:
+  memzero(result, sizeof(result));
+  memzero(mnemonic, sizeof(mnemonic));
+  return result_bits;
 }
 
 int mnemonic_check(const char *mnemonic) {
   uint8_t bits[32 + 1] = {0};
   int mnemonic_bits_len = mnemonic_to_bits(mnemonic, bits);
-  if (mnemonic_bits_len != (12 * 11) && mnemonic_bits_len != (18 * 11) &&
-      mnemonic_bits_len != (24 * 11)) {
+  if (mnemonic_bits_len != (12 * BIP39_BITS_PER_WORD) &&
+      mnemonic_bits_len != (18 * BIP39_BITS_PER_WORD) &&
+      mnemonic_bits_len != (24 * BIP39_BITS_PER_WORD)) {
     return 0;
   }
-  int words = mnemonic_bits_len / 11;
+  int words = mnemonic_bits_len / BIP39_BITS_PER_WORD;
 
   uint8_t checksum = bits[words * 4 / 3];
   sha256_Raw(bits, words * 4 / 3, bits);
@@ -222,22 +239,43 @@ void mnemonic_to_seed(const char *mnemonic, const char *passphrase,
 #endif
 }
 
-// binary search for finding the word in the wordlist
-int mnemonic_find_word(const char *word) {
-  int lo = 0, hi = BIP39_WORD_COUNT - 1;
-  while (lo <= hi) {
-    int mid = lo + (hi - lo) / 2;
-    int cmp = strcmp(word, BIP39_WORDLIST_ENGLISH[mid]);
-    if (cmp == 0) {
-      return mid;
-    }
-    if (cmp > 0) {
-      lo = mid + 1;
-    } else {
-      hi = mid - 1;
-    }
+/**
+ * @brief Constant-time memory comparison.
+ * Compares 'n' bytes, but unlike memcmp, it does not short-circuit,
+ * thus preventing timing attacks.
+ * @return `true` if the memory areas are equal, `false` otherwise.
+ */
+static bool constant_time_memeq(const void *s1, const void *s2, size_t n) {
+  const unsigned char *p1 = s1;
+  const unsigned char *p2 = s2;
+  int diff = 0;
+  for (size_t i = 0; i < n; i++) {
+    // Accumulate differences using OR to prevent early termination
+    diff |= p1[i] ^ p2[i];
+  }
+  return diff == 0;
+}
+
+/**
+ * @brief Constant-time linear search for a mnemonic word. Make sure the `word`
+ * argument is provided within at least 9 characters big buffer to avoid
+ * out-of-bounds reads.
+ */
+found_word mnemonic_find_word(const char *word) {
+  int result_index = -1;
+  size_t result_length = 0;
+  for (int i = 0; i < BIP39_WORD_COUNT; i++) {
+    const char *dict_word = BIP39_WORDLIST_ENGLISH[i];
+    size_t dict_word_len = strlen(dict_word);
+    bool is_match =  // 0 or 1 - 1 is match
+        constant_time_memeq(word, dict_word, dict_word_len + 1);
+    int8_t match_mask = -is_match;  // 0x00 or 0xFF - 0xFF is match
+    result_index =
+        (match_mask & i) + (~match_mask & result_index);  // take one of the two
+    result_length =
+        (match_mask & dict_word_len) + (~match_mask & result_length);
   }
-  return -1;
+  return (found_word){.index = result_index, .length = result_length};
 }
 
 const char *mnemonic_complete_word(const char *prefix, int len) {
```

### crypto/bip39.h
```diff
@@ -25,13 +25,18 @@
 #define __BIP39_H__
 
 #include <stdbool.h>
+#include <stddef.h>
 #include <stdint.h>
 
 #include "options.h"
 
 #define BIP39_WORD_COUNT 2048
 #define BIP39_PBKDF2_ROUNDS 2048
 
+#define BIP39_MAX_WORD_LEN 8
+#define BIP39_MAX_MNEMONIC_LEN (24 * BIP39_MAX_WORD_LEN + 23)
+#define BIP39_BITS_PER_WORD 11
+
 #if USE_BIP39_CACHE
 void bip39_cache_clear(void);
 #endif
@@ -51,7 +56,12 @@ void mnemonic_to_seed(const char *mnemonic, const char *passphrase,
                       void (*progress_callback)(uint32_t current,
                                                 uint32_t total));
 
-int mnemonic_find_word(const char *word);
+typedef struct {
+  int index;
+  size_t length;
+} found_word;
+
+found_word mnemonic_find_word(const char *word);
 const char *mnemonic_complete_word(const char *prefix, int len);
 const char *mnemonic_get_word(int index);
 uint32_t mnemonic_word_completion_mask(const char *prefix, int len);
```

### crypto/tests/test_check.c
```diff
@@ -6875,12 +6875,24 @@ START_TEST(test_mnemonic_to_bits) {
 END_TEST
 
 START_TEST(test_mnemonic_find_word) {
-  ck_assert_int_eq(-1, mnemonic_find_word("aaaa"));
-  ck_assert_int_eq(-1, mnemonic_find_word("zzzz"));
+  char word1[BIP39_MAX_WORD_LEN + 1] = "aaaa";
+  found_word record = mnemonic_find_word(word1);
+  ck_assert_int_eq(-1, record.index);
+  ck_assert_int_eq(0, record.length);
+
+  char word2[BIP39_MAX_WORD_LEN + 1] = "zzzz";
+  record = mnemonic_find_word(word2);
+  ck_assert_int_eq(-1, record.index);
+  ck_assert_int_eq(0, record.length);
+
+  char word_buf[BIP39_MAX_WORD_LEN + 1] = {0};
   for (int i = 0; i < BIP39_WORD_COUNT; i++) {
     const char *word = mnemonic_get_word(i);
-    int index = mnemonic_find_word(word);
-    ck_assert_int_eq(i, index);
+    memset(word_buf, 0, sizeof(word_buf));
+    strncpy(word_buf, word, sizeof(word_buf) - 1);
+    record = mnemonic_find_word(word_buf);
+    ck_assert_int_eq(i, record.index);
+    ck_assert_int_eq(strlen(word), record.length);
   }
 }
 END_TEST
```

### legacy/firmware/config.c
```diff
@@ -620,16 +620,6 @@ const uint8_t *config_getSeed(void) {
         return NULL;
       }
     }
-    // if storage was not imported (i.e. it was properly generated or recovered)
-    bool imported = false;
-    config_get_bool(KEY_IMPORTED, &imported);
-    if (!imported) {
-      // test whether mnemonic is a valid BIP-0039 mnemonic
-      if (!mnemonic_check(mnemonic)) {
-        // and if not then halt the device
-        error_shutdown(_("Storage failure"), _("detected."), NULL, NULL);
-      }
-    }
     char oldTiny = usbTiny(1);
     mnemonic_to_seed(mnemonic, passphrase, activeSessionCache->seed,
                      get_root_node_callback);  // BIP-0039
```

### legacy/firmware/recovery.c
```diff
@@ -529,7 +529,14 @@ void recovery_init(uint32_t _word_count, bool passphrase_protection,
 static void recovery_scrambledword(const char *word) {
   int index = -1;
   if (enforce_wordlist) {  // check if word is valid
-    index = mnemonic_find_word(word);
+    // mnemonic_find_word requires a buffer of at least 9 bytes
+    char buffer[BIP39_MAX_WORD_LEN + 1] = {0};
+    int word_len = strlen(word);
+    if (word_len <= BIP39_MAX_WORD_LEN) {
+      memcpy(buffer, word, strlen(word));
+      index = mnemonic_find_word(buffer).index;
+      memzero(buffer, sizeof(buffer));
+    }
     if (index < 0) {  // not found
       if (!dry_run) {
         session_clear(true);
```

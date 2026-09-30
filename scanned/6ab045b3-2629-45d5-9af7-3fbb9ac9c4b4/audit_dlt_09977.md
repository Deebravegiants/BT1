# [?] Litecoin: Fix travis unsigned integer overflow error

## Summary
Severity: Unknown
Chain: Litecoin
Component: litecoin-project/litecoin
Published: 2019-11-10
Source: https://github.com/litecoin-project/litecoin/commit/5836d84f2148e44025b58e9c5a311bbe37aa841b
Type: security-commit

## Details
Litecoin: Fix travis unsigned integer overflow error

## Patch
### src/crypto/scrypt.cpp
```diff
@@ -188,6 +188,7 @@ PBKDF2_SHA256(const uint8_t *passwd, size_t passwdlen, const uint8_t *salt,
 
 #define ROTL(a, b) (((a) << (b)) | ((a) >> (32 - (b))))
 
+__attribute__((no_sanitize("integer")))
 static inline void xor_salsa8(uint32_t B[16], const uint32_t Bx[16])
 {
 	uint32_t x00,x01,x02,x03,x04,x05,x06,x07,x08,x09,x10,x11,x12,x13,x14,x15;
```

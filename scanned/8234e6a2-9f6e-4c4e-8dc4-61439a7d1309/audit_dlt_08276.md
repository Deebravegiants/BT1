# [?] ballet: fix out-of-bounds read in sbpf loader

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2025-10-28
Source: https://github.com/firedancer-io/firedancer/commit/3269d1985f69cb2c0c1cc45b6be78f3dbb2c2151
Type: security-commit

## Details
ballet: fix out-of-bounds read in sbpf loader

## Patch
### src/ballet/sbpf/fd_sbpf_loader.c
```diff
@@ -608,7 +608,7 @@ fd_sbpf_r_bpf_64_relative( fd_sbpf_elf_t const *      elf,
     ulong refd_addr = 0UL;
 
     /* https://github.com/anza-xyz/sbpf/blob/v0.12.2/src/elf.rs#L1230-L1239 */
-    if( FD_UNLIKELY( fd_ulong_sat_add( r_offset, 4UL /* BYTE_LENGTH_IMMEDIATE */ )>elf_sz ) ) {
+    if( FD_UNLIKELY( fd_ulong_sat_add( imm_offset, 4UL /* BYTE_LENGTH_IMMEDIATE */ )>elf_sz ) ) {
       return FD_SBPF_ELF_ERR_VALUE_OUT_OF_BOUNDS;
     }
     refd_addr = FD_LOAD( uint, rodata+imm_offset );
```

# [?] reedsol: prevent theoretical OOB read/write

## Summary
Severity: Unknown
Chain: Solana
Component: firedancer-io/firedancer
Published: 2026-04-02
Source: https://github.com/firedancer-io/firedancer/commit/e8d5d240f3d24562f3daf3d0535493509c3d151a
Type: security-commit

## Details
reedsol: prevent theoretical OOB read/write

The "case 7UL"-case expands STORE_COMPARE( 134, ...) which accesses shred[134] or erased[134].
But both arrays only contain 134 elements, so this is an off-by-one.

However, assuming that we have a maximum of 134 (67*2) shreds, it's not possible to actually
hit the "case 7UL"-case, because this would mean that we received 128+7 = 135 shreds
for e.g. recover_128.

This also fixes the cpp/constant-array-overflow CodeQL alerts for this.

## Patch
### src/ballet/reedsol/fd_reedsol_recover_128.c
```diff
@@ -587,7 +587,6 @@ fd_reedsol_private_recover_var_128( ulong           shred_sz,
       FD_REEDSOL_GENERATE_FFT(  128, 128, ALL_VARS );
 
       switch( fd_ulong_min( shreds_remaining, 128UL ) ) {
-        case  7UL: STORE_COMPARE( 134, in06 ); FALLTHRU
         case  6UL: STORE_COMPARE( 133, in05 ); FALLTHRU
         case  5UL: STORE_COMPARE( 132, in04 ); FALLTHRU
         case  4UL: STORE_COMPARE( 131, in03 ); FALLTHRU
```

### src/ballet/reedsol/fd_reedsol_recover_16.c
```diff
@@ -306,7 +306,6 @@ fd_reedsol_private_recover_var_16( ulong           shred_sz,
       FD_REEDSOL_GENERATE_FFT(  16, 128, ALL_VARS );
 
       switch( fd_ulong_min( shreds_remaining, 16UL ) ) {
-        case  7UL: STORE_COMPARE( 134, in06 ); FALLTHRU
         case  6UL: STORE_COMPARE( 133, in05 ); FALLTHRU
         case  5UL: STORE_COMPARE( 132, in04 ); FALLTHRU
         case  4UL: STORE_COMPARE( 131, in03 ); FALLTHRU
```

### src/ballet/reedsol/fd_reedsol_recover_32.c
```diff
@@ -322,7 +322,6 @@ fd_reedsol_private_recover_var_32( ulong           shred_sz,
       FD_REEDSOL_GENERATE_FFT(  32, 128, ALL_VARS );
 
       switch( fd_ulong_min( shreds_remaining, 32UL ) ) {
-        case  7UL: STORE_COMPARE( 134, in06 ); FALLTHRU
         case  6UL: STORE_COMPARE( 133, in05 ); FALLTHRU
         case  5UL: STORE_COMPARE( 132, in04 ); FALLTHRU
         case  4UL: STORE_COMPARE( 131, in03 ); FALLTHRU
```

### src/ballet/reedsol/fd_reedsol_recover_64.c
```diff
@@ -402,7 +402,6 @@ fd_reedsol_private_recover_var_64( ulong           shred_sz,
       FD_REEDSOL_GENERATE_FFT(  64, 128, ALL_VARS );
 
       switch( fd_ulong_min( shreds_remaining, 64UL ) ) {
-        case  7UL: STORE_COMPARE( 134, in06 ); FALLTHRU
         case  6UL: STORE_COMPARE( 133, in05 ); FALLTHRU
         case  5UL: STORE_COMPARE( 132, in04 ); FALLTHRU
         case  4UL: STORE_COMPARE( 131, in03 ); FALLTHRU
```

### src/ballet/reedsol/generate_recover.py
```diff
@@ -133,7 +133,7 @@ def make_recover_var(n, max_shreds):
             cprint(f"FD_REEDSOL_GENERATE_FFT(  {n}, {n*(chunk_cnt+1):2}, ALL_VARS );")
             cprint("")
             cprint(f"switch( fd_ulong_min( shreds_remaining, {n}UL ) ) " + "{")
-            for k in range(min(n-1, potential_shreds_remaining), -1, -1):
+            for k in range(min(n, potential_shreds_remaining)-1, -1, -1):
                 fallthru = ""
                 if k>0:
                     fallthru = " FALLTHRU"
```

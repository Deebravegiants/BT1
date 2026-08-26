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

# [?] limit weight to max_uint64 to avoid overflow (#9191)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys/teku
Published: 2025-03-03
Source: https://github.com/Consensys/teku/commit/690517ee55274e476318f433f529a2656f4b27f5
Type: security-commit

## Details
limit weight to max_uint64 to avoid overflow (#9191)

fixes #9189

could be worked to larger value if we need? but this seems like a hard thing to get to currently...

Signed-off-by: Paul Harris <paul.harris@consensys.net>

* apply feedback and add safePlus as well as test cases

Signed-off-by: Paul Harris <paul.harris@consensys.net>

* make safeMax just return max_value at most.

Signed-off-by: Paul Harris <paul.harris@consensys.net>

---------

Signed-off-by: Paul Harris <paul.harris@consensys.net>

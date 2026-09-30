# [?] interpreter: fix use-after-free in Simplicity init code

## Summary
Severity: Unknown
Chain: Liquid
Component: ElementsProject/elements
Published: 2025-01-20
Source: https://github.com/ElementsProject/elements/commit/1c871c8c20a0c097232126c7d00297f2c397cfe8
Type: security-commit

## Details
interpreter: fix use-after-free in Simplicity init code

We have the code fragment `txTo.GetHash().begin()`, which takes a
transaction, computes its txid as a uint256, and then saves a pointer to
the internal data of the uint256.

However, in C++, expressions of the form a.b().c() lead to the return
value of `b` being dropped immediately after the call to `c`. This is
fine if `c` is something like `GetHex` which returns a new independently
allocated object with no pointers to its input. It is not fine for
`begin` which returns a pointer into the return value of `GetHash`.

So this fragment returns a dangling pointer, which is later used by the
Simplicity interpreter, leading to UB.

In practice this code appeared to work, possibly because the stack
layout was such that it actually did work ok. Or possibly because we
don't test with enough fidelity to tell that Simplicity's view of the
txid of a transaction was mangled.

## Patch
### src/script/interpreter.cpp
```diff
@@ -2660,7 +2660,8 @@ void PrecomputedTransactionData::Init(const T& txTo, std::vector<CTxOut>&& spent
         }
 
         rawTransaction simplicityRawTx;
-        simplicityRawTx.txid = txTo.GetHash().begin();
+        uint256 rawHash = txTo.GetHash();
+        simplicityRawTx.txid = rawHash.begin();
         simplicityRawTx.input = simplicityRawInput.data();
         simplicityRawTx.numInputs = simplicityRawInput.size();
         simplicityRawTx.output = simplicityRawOutput.data();
```

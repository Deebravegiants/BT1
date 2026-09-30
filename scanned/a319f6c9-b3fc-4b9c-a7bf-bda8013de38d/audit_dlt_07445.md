# [?] QA: Fix race condition in wallet_encryption test

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2019-07-18
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/23bc49e28cf01501e8fb8c169cad4d97d0f34f80
Type: security-commit

## Details
QA: Fix race condition in wallet_encryption test

Summary:
```
There is some imprecision probably in the internal HTTPRPCTimer class
(haven't exactly figured out where).
But we can't expect that waiting exactly 2 seconds right after calling
walletpassphrase(2) will result in a locked wallet due to the nature how
we internally handle threads/timers.

The wallet_encryption test fails regularly in CIs.
```

Backport of core PR16420
https://github.com/bitcoin/bitcoin/pull/16420/files

Test Plan:
```
for i in {1..100}
do
  ./test/functional/test_runner.py wallet_encryption
done
```

Reviewers: #bitcoin_abc, deadalnix, jasonbcox

Reviewed By: #bitcoin_abc, jasonbcox

Differential Revision: https://reviews.bitcoinabc.org/D3702

## Patch
### test/functional/wallet_encryption.py
```diff
@@ -48,7 +48,7 @@ def run_test(self):
         assert_equal(privkey, self.nodes[0].dumpprivkey(address))
 
         # Check that the timeout is right
-        time.sleep(2)
+        time.sleep(3)
         assert_raises_rpc_error(
             -13, "Please enter the wallet passphrase with walletpassphrase first",
             self.nodes[0].dumpprivkey, address)
```

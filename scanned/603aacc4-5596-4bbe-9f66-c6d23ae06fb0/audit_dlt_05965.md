# [?] Fix intermittent "fee" related crash in `rpc_blockchain.py`

## Summary
Severity: Unknown
Chain: Bitcoin Cash
Component: bitcoin-cash-node/bitcoin-cash-node
Published: 2023-03-24
Source: https://github.com/bitcoin-cash-node/bitcoin-cash-node/commit/e016eb31b1d68382f4c98997d747729fb3245761
Type: security-commit

## Details
Fix intermittent "fee" related crash in `rpc_blockchain.py`

This MR fixes an intermittent error with the rpc_blockchain functional test,
where the expected fee for transactions would not match the actual fee.
The original assertion expected the fee to always be equal to the
transaction size multiplied by the fee rate.
This is the ideal expected fee, but it will be wrong on occasion for two
reasons.
Firstly, the fees are determined by a worst-case estimate of the transaction
size (by CalculateMaximumSignedTxSize at wallet.cpp:3280).
The reason the transaction size estimate is occasionally overly conservative
is because the transaction values and fee need to be set before the transaction
can be signed.  It's only once the transaction is signed that the real size
materializes, by which time it is too late to correct the fee, hence the
discrepancy.
Secondly, fees are always rounded up to the nearest satoshi, which the
original assertion did not factor in.

Closes #469

# Changes

- Switched the assertion to use the assert_fee_amount function which was
  designed to handle such cases.
- Fleshed out documentation for ParseFixedPoint.  Based on the original
  function description, you would think that it would return a number
  equivalent to the string-encoded number being parsed.  But you would
  be off by a factor of 100,000,000 times in most cases!


# Test plan

- Convince yourself that

  while ./test/functional/test_runner.py rpc_blockchain; do sleep 0.1; done
  
  will not halt.
  Before the fix, this would take on average about 64 iteration to fail for me.

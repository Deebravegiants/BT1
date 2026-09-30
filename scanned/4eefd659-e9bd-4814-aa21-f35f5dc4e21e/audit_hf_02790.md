# [H] Curve multi exchange can be used to withdraw assets without paying fees

## Summary
Severity: High
Contest weight: 0.1771
Dataset id: 15194
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CurveMultiExchangeAssetManager::exchange() allows sending any route, which is of type Array of [initial token, pool or zap, token, pool or zap, token, ...]. The pool or zap chosen indexes are not validated, which means any contract can be specified. Thus, users can create a contract with the same interface as pool or zap and receive the amountIn there. Then, only send back a very small amount of token out to bypass the fee manager check in calculateFee() of the amount being bigger than serviceCharge + relayerRefund. The service fees will be very small and the user will get the funds right away. The poc for issue #13 contains an example of a malicious swap contract.

## Recommendation
Apply the fees when releasing assetIn instead, this way it can not be gamed.

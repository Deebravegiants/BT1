# [M] M-10 | Read Response Censoring

## Summary
Severity: Medium
Contest weight: 0.1483
Dataset id: 1994
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Because the _lzReceive function invokes the executeMessage function in a try/catch and specifically leaves behind 50,000 gas units to complete the outer function execution it is possible for a malicious actor to intentionally censor an lzRead response by executing the lzReceive function with a minimal amount of gas. This way the inner executeMessage function is not forwarded enough gas to complete execution and fails. As a result the message is added to the payloadHashes mapping in the Beacon contract. Both normal layerzero messages and layerzero read responses can be censored this way. But specifically layerzero read requests are not allowed to be retried in the Beacon contract so they are effectively censored. To pull off this attack a malicious actor can simply observe that the last required DVN has submitted their verification and then call the commitVerification and lzReceive functions on the receive library and EndpointV2 contracts accordingly.

## Recommendation
Consider adding validation at the beginning of the _lzReceive function which requires that the transaction has enough gas to complete the receive logic, ideally this validation will also account for any callback which might occur.

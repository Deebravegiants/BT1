# [?] Fix a VC crash observed in the local_testnet simulation (#3872)

## Summary
Severity: Unknown
Chain: Ethereum
Component: status-im/nimbus-eth2
Published: 2022-07-14
Source: https://github.com/status-im/nimbus-eth2/commit/2bd5d0374373fec5034d4b86df46f5a4fff193e4
Type: security-commit

## Details
Fix a VC crash observed in the local_testnet simulation (#3872)

It's not quite clear why this condition was triggered in the local
simulation, but it seems a viable scenario after the Keymanager API
is integrated in the validator client.

The user can temporarily remove all validator keys from a running
client before adding another set of keys.

## Patch
### beacon_chain/validator_client/duties_service.nim
```diff
@@ -86,6 +86,9 @@ proc pollForAttesterDuties*(vc: ValidatorClientRef,
         res.add(index)
       res
 
+  if validatorIndices.len == 0:
+    return 0
+
   var duties: seq[RestAttesterDuty]
   var currentRoot: Option[Eth2Digest]
 
```

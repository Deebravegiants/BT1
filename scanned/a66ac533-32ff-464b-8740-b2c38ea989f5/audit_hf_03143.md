# [M] Users can push any value to Collybus immedi-

## Summary
Severity: Medium
Contest weight: 0.1897
Dataset id: 17643
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can push any value to Collybus immediately if disputeWindow is less than proposeWindow.  
If disputeWindow is less than proposeWindow, users can bypass conditions (canShift) called by shift function in OptimisticOracle.sol.  
Suppose:  
• current block.timestamp = 1000  
• disputeWindow = 10  
• proposeWindow = 100 (disputeWindow is less than proposeWindow)  
• Nonce of current proposal is 0, or it's unable to dispute (proposeWindow exceeded)  
Alice can push any value to Collybus immediately:  
1. Because any users can craft nonce, Alice crafts a nonce that decodeRoundTimestamp(nonce) = 980 and calls shift.  
2. shift function will check nonce by calling canShift, but the nonce crafted by Alice will pass canPropose(nonce) because (block.timestamp - decodeRoundTimestamp(nonce) <= proposeWindow) (1000 - 980 <= 100). Thus Alice updated the proposal with a malicious value.  
3. Then Alice call shift again, now canShift will check that the nonce (it's prevNonce now) should be unable to dispute. But the nonce can pass the condition: !canDispute(prevNonce): !(block.timestamp - decodeRoundTimestamp(nonce) <= disputeWindow) (!(1000 - 980 <= 10))  
Finally, the proposal will be pushed to Collybus.  
If disputeWindow is less than proposeWindow, attacker can push any malicious value to Collybus immediately in the same block. Users may get a wrong price when calling the read function in Collybus.sol.

## Recommendation
Should check disputeWindow >= proposeWindow in constructor.

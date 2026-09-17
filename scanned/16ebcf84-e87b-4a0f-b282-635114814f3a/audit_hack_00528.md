# [H] CrossCurve incident: The cross-chain liquidity protocol CrossCurve (formerly EYWA) has confirmed that its cross-chain bridge protocol is under attack,

## Summary
Severity: High
Target: CrossCurve
Loss: $ 3,000,000
Attack method: Smart Contract Vulnerability
Published: 2026-02-01
Source: https://www.theblock.co/post/387939/crosscurve-bridge-exploited-for-approximately-3-million-across-multiple-chains-via-spoofed-messages
Type: slowmist-incident

## Details
The cross-chain liquidity protocol CrossCurve (formerly EYWA) has confirmed that its cross-chain bridge protocol is under attack, due to a vulnerability in its smart contract that was exploited, resulting in the theft of approximately USD 3 million across multiple networks. Blockchain security firm Defimon Alerts identified that the attack vector exploited a gateway verification bypass vulnerability in CrossCurve’s ReceiverAxelar contract. Analysis shows that anyone could use a forged cross-chain message to call the contract’s expressExecute function, thereby bypassing the intended gateway verification and triggering unauthorized token unlocks on the protocol’s PortalV2 contract. Subsequently, CrossCurve issued a security update regarding the $EYWA token, stating that the exploitation has been successfully contained.

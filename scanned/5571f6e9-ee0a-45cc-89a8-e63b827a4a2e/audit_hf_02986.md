# [C] The ZKT Native token can be easily compromised

## Summary
Severity: Critical
Contest weight: 0.0691
Dataset id: 16647
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The native token is a crucial part of the protocol, the most revenue will be earned through the fees collected from it. The native ZKT Token is set in the Tsunami contract constructor:
admin = msg.sender;
nativeFactory = ZKTNativeFactory(_nativeFactory);
erc20Factory = ZKTERC20Factory(_erc20Factory);
zkts.set(uint256(bytes32(bytes(nativeFactory.nativeSymbol()))),
native);
ZKTBase(native).setUnit(10000000000000000);
ZKTBase(native).setAgency(payable(msg.sender));
ZKTBase(native).setAdmin(msg.sender);
However, the newZKTNative function which is called from the ZKTNativeFactory contract is public and is missing any access control:
ZKTETH zktETH = new ZKTETH(transfer, burn);
zktETH.setAdmin(admin);
ZKT_Tsunami.md
admin. The admin can change important parameters inside ZKTBase but the worst thing is that a malicious protocol will be lost.

## Recommendation
Add access control to the newZKTNative function so that only the admin can call it.

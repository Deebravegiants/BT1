# [H] The localSwap function does not verify that the fromAsset and toAsset are different

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-28
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/57
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** 97Sabit
**Submission hash (on-chain):** 0x5172b2b61ea439c3993f2b1722b84a12c54620b402d1160471f8d11dfeba07f6
**Severity:** high

**Description:**
**Description**\
The localSwap function does not verify that the fromAsset and toAsset are different before performing a swap. What this means is that same token can be swapped for one another.

This allows an attacker to increase the balance of the toAsset before performing the swap. 

Since there is a provision for minOut, an attacker can specify an amount greater than the input amount to ensure he loses nothing.


1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystVaultAmplified.sol#L807

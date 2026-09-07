# [H] Rounding error leads to loss of tokens when transferring tokens to the contract

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-01-26
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/48
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** 97Sabit
**Submission hash (on-chain):** 0x6088f578250a0daaccace35a03351d199fd433516b65778ffafd593fe1654a51
**Severity:** high

**Description:**
**Description**\
In the underwrite function, a rounding error occurs when transferring tokens to the contract due to integer division truncating decimals.

- The tokens amount to be sent to the contract is calculated by multiplying purchasedTokens by 1035 and dividing by 1000:

```
ERC20(toAsset).safeTransferFrom(
  msg.sender,
  address(this),
  purchasedTokens * (
    UNDERWRITING_COLLATERAL_DENOMINATOR + UNDERWRITING_COLLATERAL
  ) / UNDERWRITING_COLLATERAL_DENOMINATOR  
);

```
For example:

purchasedTokens is 112.
UNDERWRITING_COLLATERAL_DENOMINATOR is 1000.
UNDERWRITING_COLLATERAL is 35.

purchasedTokens * 1035 / 1000; 

112 * 1.035 = 115.92
Solidity truncates, so 115 tokens is transferred instead of 116.


1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->
https://github.com/catalystdao/catalyst/blob/27b4d0a2bca177aff00def8cd745623bfbf7cb6b/evm/src/CatalystChainInterface.sol#L788-L795

2. **Revised Code File (Optional)**

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/48_

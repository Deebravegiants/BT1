# [M] Possible to prevent triple deposits

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-21
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/8
Type: hats-finding

## Details
**Github username:** @0xfuje
**Twitter username:** 0xfuje
**Submission hash (on-chain):** 0x29f4b8880245c61f2acd22d93c9da5a02745d7cf7d76acdbac3a210c1cb03b7a
**Severity:** medium

**Description:**
## Impact
Denial of service for particular triples of the targeted user


## Description

The `depositTriple()` function of `EthMultiVault` allows an user to deposit assets to a triple vault. However a malicious actor may prevent deposits (especially if large) if he spends `generalConfig.minDeposit`. This is because he can deposit to the triple's counter vault for the `receiver` who intends to deposit, which will make the initial user's deposit fail.
 
`EthMultiVault.sol` - `depositTriple()`
```solidity
    function depositTriple(address receiver, uint256 id)
        external
        payable
        nonReentrant
        whenNotPaused
        returns (uint256)
    {
        if (!isTripleId(id)) {
            revert Errors.MultiVault_VaultNotTriple();
        }

        if (_hasCounterStake(id, receiver)) { 
            revert Errors.MultiVault_HasCounterStake();
        }

        if (msg.value < generalConfig.minDeposit) {
            revert Errors.MultiVault_MinimumDeposit();
        }

        uint256 protocolFees = protocolFeeAmount(msg.value, id);
        uint256 userDepositAfterProtocolFees = msg.value - protocolFees;

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/8_

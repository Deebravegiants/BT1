# [M] `depositTriple()` will get `DOS'ed` if `atomDepositFraction` is set to zero

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-25
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/49
Type: hats-finding

## Details
**Github username:** @Al-Qa-qa
**Twitter username:** al_qa_qa
**Submission hash (on-chain):** 0xf503de3c895a1f52486ee6a29a3f0a290eceebac796fa312d97273f5d0470a8e
**Severity:** medium

**Description:**
**Description**\
When making a new deposit to Triple Vaults, a part of that share goes to Atoms Vaults that is linked to that Triple Vault.

[EthMultiVault.sol#L778-L779](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L778-L779)
```solidity
    function depositTriple( ... ) ... {
        ...

        // distribute atom shares for all 3 atoms that underly the triple
        uint256 atomDepositFraction = atomDepositFractionAmount(userDepositAfterprotocolFee, id);
@>   _depositAtomFraction(id, receiver, atomDepositFraction);

        return shares;
    }
```

The problem lies is that the protocol is not checking if this value is `0` or not (initialized to be `0`), which will make the transaction revert from `_depositAtomFraction()` in `_deposit()` internal function as `sharesForReceiver` will be `0` in that case.

[EthMultiVault.sol#L924-L926](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L924-L926)
```solidity
    function _deposit(address receiver, uint256 id, uint256 value) internal returns (uint256) {
        if (previewDeposit(value, id) == 0) {
            revert Errors.MultiVault_DepositOrWithdrawZeroShares();
        }
        ...
}
```

This edge case is handled correctly in `_createTriple()`.

[EthMultiVault.sol#L638-L644](https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/blob/main/src/EthMultiVault.sol#L638-L644)
```solidity
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/49_

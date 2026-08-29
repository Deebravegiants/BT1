# [M] Incorrect `eligibleAmount` for `AirdropBroker` Phase 3

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1175
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/option-airdrop/AirdropBroker.sol#L84
https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/option-airdrop/AirdropBroker.sol#L459


# Vulnerability details


`AirdropBroker` allows users to `participate()` in the airdrop and mint `aoTAP`, which can be exercised for `TAP` tokens.

However, the `eligibleAmount` to mint for phase 3 of airdrop is incorrect as it is not multiplied by `1e18` (as `TAP` is 18 decimals). That will cause the `eligibleAmount` for phase 3 to be significantly lower as it is declared as `714` in the contract.

https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/option-airdrop/AirdropBroker.sol#L84
```Solidity
    uint256 public constant PHASE_3_AMOUNT_PER_USER = 714;
```

That means the phase 3 `aoTAP` will only allow users to exercise `714` `TAP` instead of `714e18` `TAP`.
https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/option-airdrop/AirdropBroker.sol#L459
```Solidity
    function _participatePhase3(
        ...
        
        //@audit missing * 1e18
        uint256 eligibleAmount = PHASE_3_AMOUNT_PER_USER;
        uint128 discount = uint128(PHASE_3_DISCOUNT);
        oTAPTokenID = aoTAP.mint(msg.sender, expiry, discount, eligibleAmount);
```

Furthermore `exerciseOption()` will fail at the following check as `eligibleAmount < 1e18`.

https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/option-airdrop/AirdropBroker.sol#L258
```Solidity
    function exerciseOption(
        ...
        require(chosenAmount >= 1e18, "adb: Too low");
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1175_

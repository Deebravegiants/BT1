# [H] `LiquidityPool` contract can not receive `T-NFT` or ERC721 NFTs

## Summary
Severity: High
Chain: Smart contract
Component: ether-fi
Published: 2023-11-07
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/21
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Submission hash (on-chain):** 0x39e514a238fb38463ea1d7d1656c12a067c40fe174df2d6d278a6f3c5a360acf
**Severity:** high

**Description:**
**Description**\
In `LiquidityPool.sol`, `batchRegisterAsBnftHolder()` function is used BNFT players to register validators they have deposited. This function triggers a 1 ETH transaction to the beacon chain. 

The actual issue is explained below(*only relevant code is kept for simpler understanding of issue by readers/reviewers*)

```Solidity
File: src/LiquidityPool.sol

    function batchRegisterAsBnftHolder(
        bytes32 _depositRoot,
        uint256[] calldata _validatorIds,
        IStakingManager.DepositData[] calldata _registerValidatorDepositData,
        bytes32[] calldata _depositDataRootApproval,
        bytes[] calldata _signaturesForApprovalDeposit
    ) external whenNotPaused {

       // some code

        stakingManager.batchRegisterValidators(_depositRoot, _validatorIds, msg.sender, address(this), _registerValidatorDepositData, msg.sender);
        
       // some code

        }
    }
```

Under the hood, this function calls `stakingManager.batchRegisterValidators()` which is used to create validator object, mints NFTs, sets NB variables and deposits 1 ETH into beacon chain and it can be seen as below,

```Solidity
File: src/StakingManager.sol

    function batchRegisterValidators(
        bytes32 _depositRoot,
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/21_

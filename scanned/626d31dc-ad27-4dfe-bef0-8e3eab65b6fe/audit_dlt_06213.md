# [M] Malicious actor can immediately mint out all `MembershipNFT`s and prevent other users from minting

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-09
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/39
Type: hats-finding

## Details
**Github username:** @0xfuje
**Submission hash (on-chain):** 0xd8013528d4d856d092e156744798f81e276a22a1acb93c083ba1a3b55f667546
**Severity:** medium

**Description:**
## Description
The `minDepositGwei` and `mintFee`variable in `MemberShipManager` prevents an attacker from minting out all `MembershipNFT`s low cost. To set `minDepositGwei` and `mintFee` the owner of the contract has to call `setDepositAmountParams()` and `setFeeAmounts()`.

`src/MembershipManager.sol` - [`setDepositAmountParams()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L344-L351)
```solidity
    /// @notice Updates minimum valid deposit
    /// @param _minDepositGwei minimum deposit in wei
    /// @param _maxDepositTopUpPercent integer percentage value
    function setDepositAmountParams(uint56 _minDepositGwei, uint8 _maxDepositTopUpPercent) external {
        _requireAdmin();
        minDepositGwei = _minDepositGwei;
        maxDepositTopUpPercent = _maxDepositTopUpPercent;
    }
```

`src/MembershipManager.sol` - [`setFeeAmounts()`](https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/180c708dc7cb3214d68ea9726f1999f67c3551c9/src/MembershipManager.sol#L344-L351)
```solidity
    function setFeeAmounts(uint256 _mintFeeAmount, uint256 _burnFeeAmount, uint256 _upgradeFeeAmount, uint16 _burnFeeWaiverPeriodInDays) external {
        _requireAdmin();
        _feeAmountSanityCheck(_mintFeeAmount);
        _feeAmountSanityCheck(_burnFeeAmount);
        _feeAmountSanityCheck(_upgradeFeeAmount);
        mintFee = uint16(_mintFeeAmount / 0.001 ether);
        burnFee = uint16(_burnFeeAmount / 0.001 ether);
        upgradeFee = uint16(_upgradeFeeAmount / 0.001 ether);
        burnFeeWaiverPeriodInDays = _burnFeeWaiverPeriodInDays;
    }
```


The problem that allows this exploit is that the fee and deposit params are not set immediately upon contract deployment or initialization. This allows for an exploit where an attacker front-runs or simply mints out all of the `MemberShipNFT`s before the deposit params are set. This would prevent other users from minting.

The current maximum mintable tokens are set to 1000 in `MemberShipNFT.sol`:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/39_

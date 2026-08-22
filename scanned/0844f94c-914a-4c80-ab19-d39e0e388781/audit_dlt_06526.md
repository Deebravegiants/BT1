# [M] Accrued Fees Not Minted before Fee Parameters Are Updated

## Summary
Severity: Medium
Chain: Smart contract
Component: Velvet-Capital
Published: 2024-06-21
Source: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/47
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xacc9cb45bda1ecb2b6d1057c4cb978d2804d0cf9c80041c0c55f06e42a6289b4
**Severity:** medium

**Description:**
**Description**\

Each portfolio is connected with a fee module which charges and mints protocol and management fees based on current configurations and token supply. Fee modules have multiple parameters crucial for calculating the fee amount, and these parameters can be changed by the ProtocolOwner. This could result in less fee being minted to the protocol and management team.

**Attachments**

1. **Proof of Concept (PoC) File**

The `VaultManager` calls the ` _chargeFees()` internal function whenever new deposits and withdrawals occur. The fee is directly proportional to the total supply of portfolio tokens, the defined fee percentage basis points, and the time interval between the most recent deposit/withdrawal and the current timestamp. If there is no deposit or withdrawal, the fee will accrue and be minted to the team in the next deposit/withdrawal call.

```solidity
  function _chargeFees(address _user) internal {
    // Check if the sender is not a treasury account to avoid charging fees on internal transfers.
    if (
      !(_user == assetManagementConfig().assetManagerTreasury() ||
        _user == protocolConfig().velvetTreasury())
    ) {
      // Invoke the fee module to charge both protocol and management fees.
      feeModule()._chargeProtocolAndManagementFees();
    }
  }
```
https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/blob/main/contracts/core/management/FeeManager.sol#L35

The `_chargeFees()` function calculates the protocol and management fee and mints it to the corresponding address.

```solidity
  function _chargeProtocolAndManagementFees() external nonReentrant {
    uint256 _managementFee = assetManagementConfig.managementFee();
    uint256 _protocolFee = protocolConfig.protocolFee();
    uint256 _protocolStreamingFee = protocolConfig.protocolStreamingFee();
    uint256 _totalSupply = portfolio.totalSupply();
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Velvet-Capital-0x0bb0c08fd9eeaf190064f4c66f11d18182961f77/issues/47_

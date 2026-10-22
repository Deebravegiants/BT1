# [M] Fee and profit payments into RevenueSharingVault can be sandwiched

## Summary
Severity: Medium
Contest weight: 0.4480
Dataset id: 16058
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
TRNDO transfer fees and trading profits are sent to RevenueSharingVault where the shares of stakers appreciate. Rewards to stakers are paid out immediately. As a result, if large payouts are made, it can be profitable to make a flash-deposit to earn rewards without having staked TRNDO for any considerable amount of time.
Such behavior acts as a net transfer of rewards from unsophisticated to sophisticated stakers. Consider that the buy and sell fee payments to the Vault can be sandwiched within a single transaction by constructing a transaction consisting of:
1. deposit into the Vault
2. buy or sell TRNDO and incur the buy / sell fee
3. withdraw from the Vault
Payments of trading gains are harder to sandwich because they can only be triggered by an external transaction, and Blast has no mempool that allows front-running. Still, the same considerations apply that users that have staked for a short period of time can earn an outsized portion of rewards.

## Recommendation
```solidity
It is recommended to send rewards to a separate VaultDistributor contract that ensures rewards are paid out slowly. Available rewards are snapshotted and paid out linearly over a configurable timeframe. At the end of the timeframe, available rewards are snapshotted again.
This approach requires that additional functions in ERC4626 must be overridden.
Changes in RevenueSharingVault:
--- a/apps/contracts/src/tornadoToken/RevenueSharingVault.sol
+++ b/apps/contracts/src/tornadoToken/RevenueSharingVault.sol
@@ -7,12 +7,18 @@ import { ERC4626 } from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import { TornadoBlastBotToken } from "./TornadoBlastBotToken.sol";
import { BlastGasAndYield } from "../commons/BlastGasAndYield.sol";
+import {VaultDistributor} from "../VaultDistributor.sol";
+
/// @dev send tornado blast tokens to this contract to redistribute them to stakers
/// @dev treasury MUST stake a significant amount first to avoid future share/tokenAmount slippage
contract RevenueSharingVault is ERC4626, BlastGasAndYield {
+
    VaultDistributor vaultDistributor;
    constructor(
        TornadoBlastBotToken tornadoBlastToken
    ) ERC4626(tornadoBlastToken) ERC20("Staked Tornado Blast Token", "stTRNDO") {}
+
    TornadoBlastBotToken tornadoBlastToken,
+
    VaultDistributor _vaultDistributor
+
    ) ERC4626(tornadoBlastToken) ERC20("Staked Tornado Blast Token", "stTRNDO") {
+
        vaultDistributor = _vaultDistributor;
+
    }
    function _update(address from, address to, uint256 value) internal override {
        // allow mint and burn, disallow transfers
@@ -21,4 +27,32 @@ contract RevenueSharingVault is ERC4626, BlastGasAndYield {
    }
    super._update(from, to, value);
}
+
+
    function setVaultDistributor(VaultDistributor _vaultDistributor) external onlyOwner {
+
        vaultDistributor = _vaultDistributor;
+
    }
+
+
    function totalAssets() public view override returns (uint256) {
+
        return _asset.balanceOf(address(this)) + vaultDistributor.pendingRewards();
+
    }
+
+
    function deposit(uint256 assets, address receiver) public override returns (uint256) {
+
        vaultDistributor.processRewards();
+
        super.deposit(assets, receiver);
+
    }
+
+
    function mint(uint256 shares, address receiver) public override returns (uint256) {
+
        vaultDistributor.processRewards();
+
        super.mint(shares, receiver);
+
    }
+
+
    function withdraw(uint256 assets, address receiver, address owner) public override returns (uint256) {
+
        vaultDistributor.processRewards();
+
        super.withdraw(assets, receiver, owner);
+
    }
+
+
    function redeem(uint256 shares, address receiver, address owner) public override returns (uint256) {
+
        vaultDistributor.processRewards();
+
        super.redeem(shares, receiver, owner);
+
    }
}
New VaultDistributor contract:
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.25;
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";
import { VestingUtils } from "./Vesting/VestingUtils.sol";
import { ERC4626 } from "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
contract VaultDistributor is Ownable, VestingUtils {
    uint256 payoutPeriod;
    uint256 activePayoutPeriod;
    uint256 lastTimestamp;
    uint256 allPaidOutTimestamp;
    uint256 rewardBalance;
    constructor(ERC4626 _tokenizedVault) VestingUtils(_tokenizedVault) Ownable(msg.sender) {
        payoutPeriod = 1 weeks;
        lastTimestamp = block.timestamp;
        activePayoutPeriod = payoutPeriod;
        allPaidOutTimestamp = block.timestamp;
    }
    function setPayoutPeriod(uint256 newPayoutPeriod) external onlyOwner {
        require(payoutPeriod > 0, "payoutPeriod cannot be zero");
        payoutPeriod = newPayoutPeriod;
    }
    function processRewards() external {
        uint256 amountToPay = pendingRewards();
        if (amountToPay > 0) {
            vestedToken.transfer(address(tokenizedVault), amountToPay);
        }
        if (block.timestamp >= allPaidOutTimestamp) {
            activePayoutPeriod = payoutPeriod;
            allPaidOutTimestamp = block.timestamp + activePayoutPeriod;
            rewardBalance = vestedToken.balanceOf(address(this));
        }
        lastTimestamp = block.timestamp;
    }
    function pendingRewards() public view returns(uint256) {
        uint256 timestampNow = block.timestamp;
        if (block.timestamp > allPaidOutTimestamp) {
            timestampNow = allPaidOutTimestamp;
        }
        uint256 timePassed = timestampNow - lastTimestamp;
        uint256 amountToPay = rewardBalance * timePassed / activePayoutPeriod;
        return amountToPay;
    }
}
```

# [M] Sandwiched updatePower() For Higher Quantity

## Summary
Severity: Medium
Contest weight: 0.4596
Dataset id: 12461
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LuckyChip Staking protocol has a LuckyPower contract that provides an incentive mechanism that rewards the unclaimed rewards from other farming pools. The reward is calculated as 100% x "Unclaimed LC"+ 50% x "staked LC", where "Unclaimed LC" is the LC tokens earned from Farming and Bet Mining but not been claimed yet, "Staked LC" is the LC tokens staked in Liquidity Pool or Dice Table Banker. Our analysis shows the current incentive mechanism logic of providing rewards based on amount of "staked LC" could be sandwiched for higher quantity, thus higher rewards. To elaborate, we show below the related routines for the quantity calculation.

```solidity
function updatePower(address account) public override {
    require(account != address(0), "LuckyPower: account is zero address");
    for (uint256 i = 0; i < bonusInfo.length; i++) {
        BonusInfo storage bonus = bonusInfo[i];
        if (bonus.token != address(lcToken)) {
            oracle.update(bonus.token, address(lcToken));
        }
    }
    UserInfo storage user = userInfo[account];
    addPendingRewards(account);
    uint256 tmpQuantity = user.quantity;
    uint256 newQuantity = 0;
    if (address(masterChef) != address(0) && address(oracle) != address(0)) {
        (address[] memory tokens, uint256[] memory amounts, uint256[] memory pendingLcAmounts, uint256 devPending, uint256 poolLength) = masterChef.getLuckyPower(account);
        uint256 tmpLpQuantity = 0;
        uint256 tmpBankerQuantity = 0;
        uint256 tmpValue = 0;
        for (uint256 i = 0; i < poolLength; i++) {
            if (amounts[i] > 0) {
                if (EnumerableSet.contains(_lpTokens, tokens[i])) {
                    tmpValue = oracle.getLpTokenValue(tokens[i], amounts[i]);
                    tmpLpQuantity = tmpLpQuantity.add(tmpValue.mul(lpPercent).div(PERCENT_DEC)).add(pendingLcAmounts[i]);
                    newQuantity = newQuantity.add(tmpValue.mul(lpPercent).div(PERCENT_DEC)).add(pendingLcAmounts[i]);
                } else if (EnumerableSet.contains(_diceTokens, tokens[i])) {
                    tmpValue = oracle.getDiceTokenValue(tokens[i], amounts[i]);
                    tmpBankerQuantity = tmpBankerQuantity.add(tmpValue).add(pendingLcAmounts[i]);
                    newQuantity = newQuantity.add(tmpValue).add(pendingLcAmounts[i]);
                }
            }
        }
        user.lpQuantity = tmpLpQuantity;
        user.bankerQuantity = tmpBankerQuantity;
        if (devPending > 0) {
            newQuantity = newQuantity.add(devPending);
        } else {
            user.bankerQuantity = 0;
            user.lpQuantity = 0;
        }
    }
}
```

We notice the tmpValue is calculated by oracle.getLpTokenValue(tokens[i], amounts[i]) (line 205), where amounts[i] is derived from the staked token amounts from MasterChef. However, a bad actor could stake large amount tokens into the Masterchef before the calling of updateBonus() and getting a higher amounts[i] when calculating the reward from LuckyPower(). Then the bad actor would unstake the large amount of tokens from Masterchef afterwards.

## Recommendation
Only take pendingLcAmounts from MasterChef into the LuckyPower rewards calculation.

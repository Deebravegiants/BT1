# [H] DepositManager::sponsorGame should revert if the game is Cancelled or Concluded

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23469
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DepositManager::sponsorGame doesn't verify the state of the game when accepting sponsorship
amounts:
```solidity
function sponsorGame(uint256 gameId, uint256 amount) external {
    GamePool storage pool = gamePools[gameId];
    pool.totalCollectedAmount += amount;
    sponsorAmounts[msg.sender][gameId] += amount;
    emit GameSponsored(gameId, msg.sender, pool.token, amount);
    SafeERC20.safeTransferFrom(IERC20(pool.token), msg.sender, address(this), amount);
}
```

## Recommendation
DepositManager::sponsorGame should revert if the game is Cancelled or Concluded.

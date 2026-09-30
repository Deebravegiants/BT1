# [M] A malicious user can delay any user's with-

## Summary
Severity: Medium
Contest weight: 0.5823
Dataset id: 22925
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Withdrawing and transferring is cooldowned after depositing. A malicious user can delay any user's withdrawal and transfer by depositing minimum amount of token. When depositing, the lastDeposit[_recipient] is updated to block.timestamp and lastExitCooldown[_recipient] to at least 1(L810). It means that withdrawing and transferring of the _recipient is disabled at least in the same block. It only costs the value of 100000 shares, which is very cheap in practice. -Public/contracts/PoolLogic.sol#L271-L343

```solidity
function _depositFor(
    address _recipient,
    address _asset,
    uint256 _amount,
    uint256 _cooldown
) private onlyAllowed(_recipient) whenNotFactoryPaused whenNotPaused returns (uint256 liquidityMinted) {
    [...]
    require(liquidityMinted >= 100_000, "invalid liquidityMinted");
    lastExitCooldown[_recipient] = calculateCooldown(
        balanceOf(_recipient),
        liquidityMinted,
        _cooldown,
        lastExitCooldown[_recipient],
        lastDeposit[_recipient],
        block.timestamp
    );
    lastDeposit[_recipient] = block.timestamp;
    _mint(_recipient, liquidityMinted);
    [...]
}
```

-Public/contracts/PoolLogic.sol#L777-L812

```solidity
function calculateCooldown(
    uint256 currentBalance,
    uint256 liquidityMinted,
    uint256 newCooldown,
    uint256 lastCooldown,
    uint256 lastDepositTime,
    uint256 blockTimestamp
) public pure returns (uint256 cooldown) {
    [...]
    cooldown = aggregatedCooldown > newCooldown
        ? newCooldown
        : aggregatedCooldown != 0
            ? aggregatedCooldown
            : 1;
    [...]
}
```

A malicious user can delay any user's withdrawal and transfer by depositing minimum amount of token.

## Recommendation
Depositing for other users should not be allowed.

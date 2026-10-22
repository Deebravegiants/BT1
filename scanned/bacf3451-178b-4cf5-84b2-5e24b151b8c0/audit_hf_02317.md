# [M] Improper TotalSupplyCheckPoints in XOLE

## Summary
Severity: Medium
Contest weight: 0.4486
Dataset id: 12609
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.1, the OpenLeverage protocol allows users to obtain the governance xOLE tokens by locking OLE tokens. The governance token also comes with the checkpoint feature that allows to query the total supply at a specific block number. Our examination shows that the current checkpoint implementation logic can be further improved.

In particular, the actual checkpoints are maintained in the _updateTotalSupplyCheckPoints() routine, which is shown below. It comes to our attention that it simply adds a new checkpoint without maintaining the invariant of having at most a checkpoint for a particular block number. The presence of multiple checkpoints with the same block number could greatly affect the governance functionality.

```solidity
function _mint(address account, uint amount) internal {
    totalSupply = totalSupply.add(amount);
    balances[account] = balances[account].add(amount);
    emit Transfer(address(0), account, amount);
    if (delegates[account] == address(0)) {
        delegates[account] = account;
        _moveDelegates(address(0), delegates[account], amount);
        _updateTotalSupplyCheckPoints();
    }
}

function _burn(address account) internal {
    uint burnAmount = balances[account];
    totalSupply = totalSupply.sub(burnAmount);
    balances[account] = 0;
    emit Transfer(account, address(0), burnAmount);
    _moveDelegates(delegates[account], address(0), burnAmount);
    _updateTotalSupplyCheckPoints();
}

function _updateTotalSupplyCheckPoints() internal {
    uint32 blockNumber = safe32(block.number, "block number exceeds 32 bits");
    totalSupplyCheckpoints[totalSupplyNumCheckpoints] = Checkpoint(blockNumber, totalSupply);
    totalSupplyNumCheckpoints = totalSupplyNumCheckpoints + 1;
}
```

## Recommendation
Correct the above checkpoint implementation to ensure there is at most a checkpoint for a block number.

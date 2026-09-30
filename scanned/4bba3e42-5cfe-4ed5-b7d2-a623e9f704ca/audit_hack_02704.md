# [M] Cancel () may lose user funds

## Summary
Severity: Medium
Reporter: 8olidity
Source: https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L128-L136
Type: audit-issue

## Details
# Cancel () may lose user funds

## Summary
Cancel () may lose user funds
## Vulnerability Detail
https://github.com/sherlock-audit/2022-09-knox/blob/main/knox-contracts/contracts/queue/Queue.sol#L128-L136
Cancel() is to redeem the amout specified by currentTokenId
```solidity
    function cancel(uint256 amount) external nonReentrant {
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();
        // burns the callers claim token
        _burn(msg.sender, currentTokenId, amount);
        // refunds the callers deposit
        ERC20.safeTransfer(msg.sender, amount);
        uint64 epoch = QueueStorage._getEpoch();
        emit Cancel(epoch, msg.sender, amount);
    }
```
Let's say 10 years later, currentTokenId is no longer the same as Deposit was then. So the user doesn't get the previous money when he calls Cancel again
## Impact
lose user funds
## Code Snippet
```solidity
    function cancel(uint256 amount) external nonReentrant {
        uint256 currentTokenId = QueueStorage._getCurrentTokenId();
        // burns the callers claim token
        _burn(msg.sender, currentTokenId, amount);
        // refunds the callers deposit
        ERC20.safeTransfer(msg.sender, amount);
        uint64 epoch = QueueStorage._getEpoch();
        emit Cancel(epoch, msg.sender, amount);
    }
```
## Tool used
vscode
Manual Review

## Recommendation
Cancel() can specify the currentTokenId

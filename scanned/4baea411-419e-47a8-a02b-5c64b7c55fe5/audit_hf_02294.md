# [M] Proper Handling of reward() in RewardTheAuthor

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 12517
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RewardTheAuthor contract provides a reward() routine for the user to send rewards to the author, and a claim() routine for the author to claim the rewards from the user. To elaborate, we show below the related routines.
```solidity
/**
 * @dev Reward the designated author
 * @param target the author
 * @param token the token to be rewarded
 * @param postType the post type
 * @param postId the post id
 * @param amount Amount to be rewarded
 */
function reward(
    address target,
    IERC20 token,
    uint256 postType,
    uint64 postId,
    uint256 amount
) public payable {
    require(_supportTokens.contains(address(token)), "Unsupported token");
    if (msg.value > 0) {
        require(address(token) == address(_weth), "bad params");
        _weth.deposit{value: msg.value}();
        amount = msg.value;
    } else {
        uint256 oldBal = token.balanceOf(address(this));
        token.safeTransferFrom(msgSender(), address(this), amount);
        amount = token.balanceOf(address(this)).sub(oldBal);
        require(amount > 0, "bad amount");
    }
    uint256 pending = _userRewards[msgSender()][address(token)];
    _userRewards[msgSender()][address(token)] = pending.add(amount);
    _rewardId++;
    emit Reward(
        _rewardId,
        msgSender(),
        target,
        address(token),
        postType,
        postId,
        amount,
        block.timestamp
    );
}

function claim(address token) public {
    uint256 pending = _userRewards[msgSender()][token];
    if (pending == 0) return;
    _userRewards[msgSender()][token] = 0;
    _userClaimedRewards[msgSender()][address(token)] = _userClaimedRewards[msgSender()][address(token)].add(pending);
    IERC20(token).safeTransfer(msgSender(), pending);
    emit Claim(msgSender(), token, pending);
}
```
We notice the funds deposited into the contract via reward() is counted into _userRewards[msgSender()][address(token)] rather than _userRewards[target][address(token)]. This will only allow the users to withdraw the funds deposited by themselves, not by the rewarded author.

## Recommendation
Proper handling of reward() in the RewardTheAuthor contract.

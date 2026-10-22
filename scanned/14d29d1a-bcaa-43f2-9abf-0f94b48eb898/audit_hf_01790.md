# [H] Attacker can call sweepRewardToken

## Summary
Severity: High
Contest weight: 0.6883
Dataset id: 9813
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in a reward‑sweeping routine that moves any unprotected token balance held by the contract to a designated bribes processor address. The routine is invoked through a public function that first checks that the caller is either governance or a strategist and that the token is not on a protected list, then obtains the full token balance of the contract and forwards it to an internal handler. The handler decides, based on the token type, whether to route the amount to a Badger‑tree or, for all other tokens, to the bribes processor via a low‑level safeTransfer call. Crucially, the code does not verify that the bribes processor address is non‑zero before performing the transfer. Because the bribes processor variable is initialised to the zero address and can be explicitly set to zero by the governance role, there exists a state in which the address equals 0x0. When that state is reached, any execution of the sweep function will cause the contract to transfer its entire reward token balance to the zero address, effectively burning the tokens. An attacker who can trigger the sweep while the processor address is zero can therefore cause a total loss of the accumulated rewards. The root cause is a missing validation of an external address prior to a token transfer, combined with the ability for a privileged role to set the address to an unsafe value. This flaw is subtle because ERC‑20 transfers to address(0) are technically allowed; they simply result in token destruction without emitting a distinct warning, and the contract only logs a generic RewardsCollected event, making the loss difficult to detect from the contract’s perspective. The impact is the disappearance of all reward tokens that users expect to receive, breaking the accounting assumptions of the protocol and diminishing the value of the reward pool. The issue manifests whenever the bribes processor variable is zero—either by default or after an intentional governance change—and the sweep function is called. It primarily affects token holders and the protocol’s economic guarantees. The flaw was uncovered during a security audit when the logic of the sweep function and the default value of the bribes processor variable were examined. To remediate the issue, the contract should enforce a non‑zero address check before any transfer to the bribes processor, either by adding a require statement in the internal _sendTokenToBribesProcessor function or by initializing the processor to a safe, immutable address. Alternatively, the sweep function could be restricted to a role that cannot set the processor to zero, or the transfer could be guarded with a fallback that redirects tokens to a safe vault when the target address is invalid. Implementing such validation restores the intended accounting flow and prevents accidental or malicious token burns.

## Proof of Concept
The default value of `bribesProcessor` is `0x0` and `governance` can set the value to `0x0` at any time. Rewards are stacking in contract address and they are supposed to send to `bribesProcessor`.

This is `sweepRewardToken()` and `_handleRewardTransfer()` and `_sendTokenToBribesProcessor()` code:

```solidity
/// @dev Function to move rewards that are not protected
/// @notice Only not protected, moves the whole amount using _handleRewardTransfer
/// @notice because token paths are hardcoded, this function is safe to be called by anyone
/// @notice Will not notify the BRIBES_PROCESSOR as this could be triggered outside bribes
function sweepRewardToken(address token) public nonReentrant {
    _onlyGovernanceOrStrategist();
    _onlyNotProtectedTokens(token);

    uint256 toSend = IERC20Upgradeable(token).balanceOf(address(this));
    _handleRewardTransfer(token, toSend);
}

function _handleRewardTransfer(address token, uint256 amount) internal {
    // NOTE: BADGER is emitted through the tree
    if (token == BADGER) {
        _sendBadgerToTree(amount);
    } else {
        // NOTE: All other tokens are sent to bribes processor
        _sendTokenToBribesProcessor(token, amount);
    }
}

function _sendTokenToBribesProcessor(address token, uint256 amount) internal {
    // TODO: Too many SLOADs
    IERC20Upgradeable(token).safeTransfer(address(bribesProcessor), amount);
    emit RewardsCollected(token, amount);
}
```

As you can see calling `sweepRewardToken()` eventually (`sweepRewardToken() -> _handleRewardTransfer() -> _sendTokenToBribesProcessor()`) would transfer reward funds to `bribesProcessor` and there is no check that `bribesProcessor!=0x0` in execution follow. so attacker can call `sweepRewardToken()` when `bribesProcessor` is `0x0` and contract will lose all reward tokens.

## Recommendation
Check the value of `bribesProcessor` in `_sendTokenToBribesProcessor()`.

A transfer to address 0 would cause a loss, we should have a check or add a safe default (governance for example).

Mitigated by adding a 0 check.

# [H] All funds can be stolen from FixedStrikeOp-

## Summary
Severity: High
Contest weight: 0.7836
Dataset id: 20195
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Hence this single contract holds significant payout/quote tokens as collateral. Also the deploy, create & exercise functions of this contract can be called by anyone. This is how the create function looks like:
```solidity
function create(
    uint256 amount_
) external override nonReentrant {
    ...
    if (call) {
        ...
    } else {
        payoutToken.decimals());
        ...
    }
    optionToken.mint(msg.sender, amount_);
}
```
Exercise function:
```solidity
function exercise(
    uint256 amount_
) external override nonReentrant {
    ...
    payoutToken.decimals());
    if (msg.sender != receiver) {
        ...
    }
    optionToken.burn(msg.sender, amount_);
    if (call) {
        ...
    } else {
    }
}
```
Consider this attack scenario:
• An attacker can create a malicious payout token of which he can control the decimals.
• The attacker calls deploy to create an option token with malicious payout token and DAI as quote token and put option type.
• Make payoutToken.decimals return a large number and call create. So 0 DAI will be pulled from the attacker's account but he will receive X option token.
• Make payoutToken.decimals return a small value and call reclaim. The amount of quote tokens to reclaim is calculated as a very high number (which represents number of DAI tokens). So he will receive huge amount of DAI against his X option tokens when exercise the option or when reclaim the token.
```solidity
// Transfer remaining collateral to receiver
uint256 amount = optionToken.totalSupply();
if (call) {
    payoutToken.safeTransfer(receiver, amount);
} else {
    // Calculate amount of quote tokens equivalent to amount at strike price
    payoutToken.decimals());
}
```
Hence, the attacker was able to drain all DAI tokens from the contract. The cost of attack is negligible (only gas cost). High impact, high likelihood.

## Recommendation
Consider storing the payoutToken.decimals value locally instead of fetching it real-time on all exercise or reclaim calls. Or support payout token and quote token whitelist; if the payout token and quote token are permissionless created, there will always be high risk.

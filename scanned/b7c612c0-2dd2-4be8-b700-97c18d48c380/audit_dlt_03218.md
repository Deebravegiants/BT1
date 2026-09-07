# [M] Fee-on-transfer token donations in `Shelter` break withdrawals

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-02-concur
Published: 2022-02-09
Source: https://github.com/code-423n4/2022-02-concur-findings/issues/180
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-02-concur/blob/72b5216bfeaa7c52983060ebfc56e72e0aa8e3b0/contracts/Shelter.sol#L34


# Vulnerability details

The `Sheler.donate` function `transferFrom`s `_amount` and adds the entire `_amount` to `savedTokens[_token]`.
But the actual received token amount from the transfer can be less for fee-on-transfer tokens.

The last person to withdraw will not be able to as `withdraw` uses a share computation for the entire `savedTokens[_token]` amount.
The calculated `amount` will then be higher than the actual contract balance.

```solidity
function donate(IERC20 _token, uint256 _amount) external {
    require(activated[_token] != 0, "!activated");
    savedTokens[_token] += _amount;
    // @audit fee-on-transfer. then fails for last person in `withdraw`
    _token.safeTransferFrom(msg.sender, address(this), _amount);
}

function withdraw(IERC20 _token, address _to) external override {
    // @audit percentage on storage var, not on actual balance
    uint256 amount = savedTokens[_token] * client.shareOf(_token, msg.sender) / client.totalShare(_token);
    // @audit amount might not be in contract anymore as savedTokens[_token] is over-reported
    _token.safeTransfer(_to, amount);
}
```

## Recommended Mitigation Steps
In `donate`, add only the actual transferred amounts (computed by `post-transfer balance - pre-transfer balance`) to `savedTokens[_token]`.

# [M] [M] Lack of Authorization on withdraw_underlying_to_claim() could lead to unexpected loss of profits

## Summary
Severity: Medium
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# [M] Lack of Authorization on withdraw_underlying_to_claim() could lead to unexpected loss of profits

## Summary

The `withdraw_underlying_to_claim` function in theVault contract lacks authorization. Any address can call this function to withdraw all excess share and mark the amount withdrawn as claimable, lead to a decrease in fund efficiency.

## Vulnerability Detail

The `withdraw_underlying_to_claim` function allows anyone to withdraw excess shares from Alchemix and mark them as claimable without authorization. 

Anyone can call `withdraw_underlying_to_claim` to withdraw excess shares, and the withdrawn amount will immediately go back to the protocol, stopping earning profits to pay off debt. However, since the withdrawn amount belongs to all shareholders, most of it is likely to not be withdrawn in the short term. If these funds remain in Alchemix, they can continue to earn interest.

## Impact

The `withdraw_underlying_to_claim` function can be called by anyone to withdraw excess shares from Alchemix, causing a reduction in the efficiency of the protocol as the withdrawn funds may not be claimed by shareholders in a timely manner. 

In addition, malicious users may deliberately select a time when yieldToken is losing value or when the market is unstable to call the function, causing excessive loss of profit upon redemption.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404

```vyper=393
@external
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```

## Tool used

Manual Review / ChatGPT PLUS

## Recommendation

It is recommended to add proper authorization to the withdraw_underlying_to_claim function. 

One possible solution could be to allow only authorized roles to call this function, such as the NFT holder or a group of token holders who have voted to trigger the function. 

Alternatively, a time-based mechanism could be used to automatically claim the funds after a certain period.

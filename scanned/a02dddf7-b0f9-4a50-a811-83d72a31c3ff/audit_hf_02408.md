# [M] Possible Costly LPs From Improper Vault Initialization

## Summary
Severity: Medium
Contest weight: 0.4629
Dataset id: 12959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function _issueSharesForAmount(address _to, uint256 _amount) internal returns (uint256) {
    uint256 shares = 0;
    // Issues _amount Vault shares to _to.
    // Shares must be issued prior to taking on new collateral, or
    // calculation will be wrong. This means that only *trusted* tokens
    // (with no capability for exploitative behavior) can be used.
    if (totalSupply() > 0) {
        // Mint amount of shares based on what the Vault is managing overall
        // NOTE: if sqrt(token.totalSupply()) > 1e39, this could potentially revert
        shares = _amount.mul(totalSupply()).div(_totalAssets());
    } else {
        shares = _amount;
    }
    _mint(_to, shares);
    return shares;
}
```
Specifically, when the pool is being initialized, the share value directly takes the value of shares = _amount (line 538), which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated shares = 1 WEI. With that, the actor can further deposit a huge amount of token with the goal of making the share extremely expensive. An extremely expensive share can be very inconvenient to use as a small number of 1 Wei may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable. Note other routines, i.e., HandsOn::enter() and HandsOnByProxy::enter(), share the same issue.

## Recommendation
Revise current execution logic of share calculation to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.

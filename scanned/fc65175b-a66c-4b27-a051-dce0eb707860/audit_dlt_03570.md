# [M] Fee on transfer tokens can lead to incorrect approval

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-defiprotocol
Published: 2021-09-22
Source: https://github.com/code-423n4/2021-09-defiprotocol-findings/issues/236
Type: code-finding

## Details
# Handle

hrkrshnn


# Vulnerability details

## Fee on transfer tokens can lead to incorrect approval

The
[createBasket](https://github.com/code-423n4/2021-09-defiProtocol/blob/main/contracts/contracts/Factory.sol#L106)
function does not account for tokens with fee on transfer.

``` solidity
function createBasket(uint256 idNumber) external override returns (IBasket) {
    // ...
    for (uint256 i = 0; i < bProposal.weights.length; i++) {
        IERC20 token = IERC20(bProposal.tokens[i]);
        token.safeTransferFrom(msg.sender, address(this), bProposal.weights[i]);
        token.safeApprove(address(newBasket), bProposal.weights[i]);
    }
    // ...
}
```

The function `safeTransferFrom` may not transfer exactly
`bProposal.weights[i]` amount of tokens, for tokens with a fee on
transfer. This means that the `safeApprove` call in the next line would
be approving more tokens than what was received, leading to accounting
issues.

### Recommended Mitigation Steps

It is recommended to find the balance of the current contract before and
after the `transferFrom` to see how much tokens were received, and
approve only what was received.

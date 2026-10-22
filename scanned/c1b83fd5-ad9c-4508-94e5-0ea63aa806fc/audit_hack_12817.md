# [M] swap() function allows malicious users to steal tokens

## Summary
Severity: Medium
Reporter: XDZIBEC
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67C5-L69C1
Type: audit-issue

## Details
# swap() function allows malicious users to steal tokens

## Summary
the `transferFrom` and `approve` functions of the ERC20 token will always succeed. If these functions fail for some reason as insufficient balance or allowance, then  the contract will still proceed and this might lead to unexpected behavior. 
## Vulnerability Detail
```solidity
def swap(
    _token_in: address,
    _token_out: address,
    _amount_in: uint256,
    _min_amount_out: uint256,
) -> uint256:
    ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
    ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)

    if self.direct_route[_token_in][_token_out] != 0:
        return self._direct_swap(_token_in, _token_out, _amount_in, _min_amount_out)
    else:
        return self._multi_hop_swap(_token_in, _token_out, _amount_in, _min_amount_out)

```
this is the two line that explain in the summary :

```solidity
    ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
    ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)
```
## Impact
- this can  lead to financial losses for the users whose tokens were stolen.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L67C5-L69C1
## Tool used

Manual Review

## Recommendation
- use check to ensure the return values of these functions

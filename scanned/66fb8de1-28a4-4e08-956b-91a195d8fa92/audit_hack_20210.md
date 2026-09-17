# [H] 5.2.14reimburseLiquidityFeessend tokens twice

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BridgeFacet.sol#L644-L675, SponsorVault.sol#L197-L226, ITokenExchange.sol#L18-L
**Description:** The functionreimburseLiquidityFees()is called from theBridgeFacet, making themsg.sender
within this function to beBridgeFacet.
When usingtokenExchangesviaswapExactIn()tokens are sent tomsg.sender, which is theBridgeFacet. Then,
tokens are sent again tomsg.senderviasafeTransfer(), which is also theBridgeFacet.
Therefore, tokens end up being sent to theBridgeFacettwice.
Note: the check...balanceOf(...) != starting + sponsoredshould fail too.
Note: The fix in C4 seems to introduce this issue: code4rena-


```
contract BridgeFacet is BaseConnextFacet {
function _handleExecuteTransaction(... ) ... {
...
uint256 starting = IERC20(_asset).balanceOf(address(this));
...
(bool success, bytes memory data) = address(s.sponsorVault).call(
abi.encodeWithSelector(s.sponsorVault.reimburseLiquidityFees.selector, _asset, _args.amount,
,! _args.params.to)
);
if (success) {
uint256 sponsored = abi.decode(data, (uint256));
// Validate correct amounts are transferred
if (IERC20(_asset).balanceOf(address(this)) != starting + sponsored) { // this should
,! fail now
revert BridgeFacet__handleExecuteTransaction_invalidSponsoredAmount();
}
...
}
...
}
}
contract SponsorVault is ISponsorVault, ReentrancyGuard, Ownable {
function reimburseLiquidityFees(... ) {
if (address(tokenExchanges[_token]) != address(0)) {
...
sponsoredFee = tokenExchange.swapExactIn{value: amountIn}(_token, msg.sender); // send to
,! msg.sender
} else {
...
}
...
IERC20(_token).safeTransfer(msg.sender, sponsoredFee);// send again to msg.sender
}
}
interface ITokenExchange {
/**
* @notice Swaps the exact amount of native token being sent for a given token.
* @param token The token to receive
* @param recipient The recipient of the token
* @return The amount of tokens resulting from the swap
*/
function swapExactIn(address token, address recipient) external payable returns (uint256);
}
```
**Recommendation:** Doublecheck the code to see what the intended behavior is.
**Connext:** Solved in PR 1551.
**Spearbit:** Verified.

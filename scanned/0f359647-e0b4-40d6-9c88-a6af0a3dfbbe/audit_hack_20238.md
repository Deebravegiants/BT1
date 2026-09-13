# [M] 5.2.9 What if the receiver of Axelar_executeWithToken()doesn’t claim all tokens

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** Executor.sol#L293-L
**Description:** The function_executeWithToken() approves tokens and then callscallTo. If that contract doesn’t
retrieve the tokens then the tokens stay within theExecutorand are lost. Also see: "Remaining tokens can be
sweeped from the LiFi Diamond or theExecutor"
contract Executor is IAxelarExecutable, Ownable, ReentrancyGuard, ILiFi {
function _executeWithToken(...) ... {
...
// transfer received tokens to the recipient
IERC20(tokenAddress).approve(callTo, amount);
(bool success, ) = callTo.call(callData);
...
}
}

**Recommendation:** Consider sending the remaining tokens to a recovery address.
Document the token handling in AxelarFacet.md
**LiFi:** Fixed with PR #62.
**Spearbit:** Verified.

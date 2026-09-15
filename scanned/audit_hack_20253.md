# [M] 5.2.1 Limit possibilities ofrecoverERC20().

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** MultiMerkleDistributor.sol#L296-L300, QuestBoard.sol#L986-L

**Description:** Function recoverERC20()in contract MultiMerkleDistributor.solallows the retrieval of all
ERC20 tokens from theMultiMerkleDistributor.solwhereas the comment indicates it is only meant to retrieve
those tokens that have been sent by mistake.

Allowing to retrieve all tokens also enables the retrieval of legitimate ones. This way rewards cannot be collected
anymore. It could be seen as allowing a rug pull by the project and should be avoided.

In contrast, functionrecoverERC20()in contractQuestBoard.soldoes prevent whitelisted tokens from being re-
trieved.

Note: The project could also add a merkle tree that allows for the retrieval of legitimate tokens to their own
addresses.


```
* @notice Recovers ERC2O tokens sent by mistake to the contract
contract MultiMerkleDistributor is Ownable {
function recoverERC20(address token, uint256 amount) external onlyOwner returns(bool) {
IERC20(token).safeTransfer(owner(), amount);
return true;
}
}
```
```
contract QuestBoard is Ownable, ReentrancyGuard {
function recoverERC20(address token, uint256 amount) external onlyOwner returns(bool) {
require(!whitelistedTokens[token], "QuestBoard: Cannot recover whitelisted token");
IERC20(token).safeTransfer(owner(), amount);
return true;
}
}
```
**Recommendation:** Prevent the retrieval of legitimate tokens. Because it is not possible to enumeratequestRe-
wardToken[]to identify legitimate tokens, an extra data structure is needed. Also be aware of dual entry point
tokens.

**Paladin:** Implemented in #16.

**Spearbit:** Acknowledged.

# [M] Arbitrary Share Increment in Base Tokens

## Summary
Severity: Medium
Contest weight: 0.4598
Dataset id: 11776
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BTC+ is an innovative approach that addresses current limitations of BTC-related tokens. Speciﬁcally, BTC-pegged tokens maintain a stable peg against native BTC and token holders must seek for yields across various applications while bearing exorbitant transaction fees associated with allocation adjustments. BTC LP tokens include vault share tokens from current farming solutions and generate proﬁts and socialize costs for their holders, but lose their peg against BTC. In the following, we examine the ERC20 implementation of BTC+ that both maintains its peg to BTC and provide global interest to all token holders. The key relies on the unique recurring positive rebasing mechanism from accrued interest. In the following, we report an issue in the underlying tokenization logic that allows for arbitrary balance increments. Speciﬁcally, the base token is inherited from the ERC20Upgradeable contract with an overwritten _transfer() routine to apply necessary rebasing from accrued interest. To elaborate, we show below the _transfer() routine.

```solidity
/**
 * @dev Moves tokens amount from sender to recipient.
 */
function _transfer(address _sender, address _recipient, uint256 _amount) internal virtual override {
    // Rebase first to make index up-to-date
    rebase();
    uint256 _shareToTransfer = _amount.mul(WAD).div(index);
    uint256 _oldSenderShare = userShare[_sender];
    uint256 _newSenderShare = _oldSenderShare.sub(_shareToTransfer, "insufficient share");
    uint256 _oldRecipientShare = userShare[_recipient];
    uint256 _newRecipientShare = _oldRecipientShare.add(_shareToTransfer);
    uint256 _totalShares = totalShares;
    userShare[_sender] = _newSenderShare;
    userShare[_recipient] = _newRecipientShare;
    emit UserShareUpdated(_sender, _oldSenderShare, _newSenderShare, _totalShares);
    emit UserShareUpdated(_recipient, _oldRecipientShare, _newRecipientShare, _totalShares);
}
```

It comes to our attention that this routine does not properly handle a corner case when both the sender and the recipient refer to the same account. As a result, the account's balance userShare[_recipient] (line 225) can be always incremented without eﬀecting the deduction at line 224. With an increased userShare, the malicious actor can drain all funds in the current pools.

## Recommendation
Revise the _transfer() logic to properly handle the corner case when _sender == _recipient.

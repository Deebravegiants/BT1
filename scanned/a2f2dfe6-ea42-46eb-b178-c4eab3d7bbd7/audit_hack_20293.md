# [H] 5.2.1 Missing owner check onfromwhen transferring tokens

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** OrderNFT.sol#L
**Description:** TheOrderNFT.transferFrom/safeTransferFromuse the internal_transferfunction. While they
check approvals onmsg.senderthrough_isApprovedOrOwner(msg.sender, tokenId), it is never checked that
the specifiedfromparameter is actually the owner of the NFT.
An attacker can decrease other users' NFT balances, making them unable to cancel or claim their NFTs and
locking users' funds. The attacker transfers their own NFT passing the victim asfromby callingtransfer-
From(from=victim, to=attackerAccount, tokenId=attackerTokenId). This passes the_isApprovedOrOwner
check, but reducesfrom's balance.
**Recommendation:** Add the following check to_transfer
require(ownerOf(tokenId) == from, Errors.ACCESS);

**Clober:** Fixed PR 310.
**Spearbit:** Verified. Ownership check added.

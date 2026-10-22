# [M] `KUMABondToken.approve`

## Summary
Severity: Medium
Contest weight: 0.5824
Dataset id: 18125
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an inconsistency in the blacklist enforcement of the KUMABondToken contract. The approve function allows a token approval to be recorded even when the owner of the tokenId is blacklisted because it only checks that the caller (msg.sender) and the target address (to) are not blacklisted, but it does not verify that the current token owner is also not blacklisted. This missing check creates a logical flaw: a user who holds a bond token can be blacklisted after granting a blanket approval (setApprovalForAll) to an operator, and that operator can subsequently call approve on behalf of the blacklisted owner to grant another address permission to manage the token. The exploit scenario proceeds as follows: (1) a legitimate user obtains a bond token, (2) the user authorizes an operator for all of their tokens, (3) the user is later added to the blacklist, (4) the previously authorized operator calls approve to allow a third party to operate on the blacklisted user's token. Because the approve function does not revert on a blacklisted owner, the approval succeeds, violating the intended security policy that blacklisted accounts should be unable to transfer or delegate control of their assets. From a user’s perspective the symptom is that a token belonging to a blacklisted account can still be approved for another address, leading to unexpected permission grants and potentially enabling unauthorized transfers. The impact is a breach of the protocol’s accounting assumptions: funds that should be frozen may become movable through delegated approvals, undermining trust in the blacklist mechanism. The issue was discovered during a formal audit when a test case reproduced the scenario and observed that approve did not revert for a blacklisted owner. It is subtle because the approve function appears to perform the usual blacklist checks on the caller and recipient, so developers may assume the owner is implicitly covered by the transferFrom checks, which is not the case. The recommended remediation is to add an explicit notBlacklisted check on the token’s owner (ownerOf(tokenId)) within the approve function, ensuring that any attempt to approve a token owned by a blacklisted address reverts, thereby aligning approve with the rest of the contract’s blacklist enforcement and restoring the intended security guarantees.

## Proof of Concept
[KUMABondToken.approve()](https://github.com/code-423n4/2023-02-kuma/blob/3f3d2269fcb3437a9f00ffdd67b5029487435b95/src/mcag-contracts/KUMABondToken.sol#L143) only checks if `msg.sender` and `to` are not blacklisted. It doesn’t check if the owner of the `tokenId` is not blacklisted.

For example, the following scenario allows a blacklisted user’s bond token to be approved:

1. User A have a bond token bt1.
2. User A calls `KUMABondToken.setApprovalForAll(B, true)`, and user B can operate on all user A’s bond tokens.
3. User A is blacklisted.
4. User B calls `KUMABondToken.approve(C, bt1)` to approve user C to operate on bond token bt1.

## Recommendation
`KUMABondToken.approve()` should revert if the owner of the tokenId is blacklisted:

```solidity
diff --git a/src/mcag-contracts/KUMABondToken.sol b/src/mcag-contracts/KUMABondToken.sol
index 569a042..906fe7b 100644
--- a/src/mcag-contracts/KUMABondToken.sol
+++ b/src/mcag-contracts/KUMABondToken.sol
@@ -146,6 +146,7 @@ contract KUMABondToken is ERC721, Pausable, IKUMABondToken {
         whenNotPaused
         notBlacklisted(to)
         notBlacklisted(msg.sender)
+        notBlacklisted(ERC721.ownerOf(tokenId))
     {
         address owner = ERC721.ownerOf(tokenId);
```

The Warden has shown an inconsistency in implementation for the blacklist functionality.

Because a transfer would still be broken, due to `transferFrom` performing a check on all accounts involved, I agree with Medium Severity.

We confirmed this issue in a test and intend to fix it:

```solidity
function test_approve_RevertWhen_TokenOwnerBlacklistedAndApproveCalledByOperator() external {
    _kumaBondToken.issueBond(_alice, _bond);
    vm.prank(_alice);
    _kumaBondToken.setApprovalForAll(address(this), true);
    _blacklist.blacklist(_alice);
    vm.expectRevert(abi.encodeWithSelector(Errors.BLACKLIST_ACCOUNT_IS_BLACKLISTED.selector, _alice));
    _kumaBondToken.approve(_bob, 1);
}
```

<https://github.com/code-423n4/2023-02-kuma/pull/4>

**Status:** Mitigation confirmed by [0xsomeone](https://github.com/code-423n4/2023-03-kuma-mitigation-contest-findings/issues/19), [0x52](https://github.com/code-423n4/2023-03-kuma-mitigation-contest-findings/issues/12), and [hihen](https://github.com/code-423n4/2023-03-kuma-mitigation-contest-findings/issues/2).

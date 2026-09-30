# [M] Address approved by user in BorrowerNFT for

## Summary
Severity: Medium
Contest weight: 0.2472
Dataset id: 23030
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Insufficient data verification in Permit2Manager allows to break security control and front-run the user using his permit to deposit funds into his NFT and deposit them into the attacker's NFT instead.
In more details: BorrowerNFT allows any user to mint NFT's, which creates a borrower account and allows the user to control this account via the BorrowerNFT.modify calls. User can either call modify himself, or approve any address to call it on his behalf. The user can either approve address for all of his NFTs, or he can approve address for his individual NFTs. Notice: if the user approves some address to one of his NFTs, this address must not have any control condition, allowing the address approved by user to one NFT to steal user funds from the other NFTs (even when not approved for them).
Suppose attacker address is approved by user to NFT1. And then the same user calls BorrowerNFT.modify for NFT2 with Permit2Manager in the calldata. Attacker can extract the user's permit to deposit funds into NFT2 and front-run the transaction with his own transaction calling BorrowerNFT.modify for NFT1 with the same owner (user), with Permit2Manager and permit from user's transaction (but setting the to address to NFT1).
Here are all the security control checks, all of them will be passed by the attacker's transaction:
1. modify first verifies if attacker is authorized, he is not, so authorized is set to false:
bool authorized = msg.sender == owner || isApprovedForAll[owner][msg.sender];
2. modify checks if attacker is approved to control the NFT1, he was approved, so this require passes correctly:
if (!authorized) require(msg.sender == getApproved[tokenId], "NOT_AUTHORIZED");
3. Next modify calls borrower.modify (where borrower corresponds to NFT1) with Permit2Manager.callback, which performs its own check. First check passes (msg.sender is NFT1 borrower which is registered as borrower in the FACTORY and the owner of this borrower is BORROWER_NFT):
require(FACTORY.isBorrower(msg.sender) && owner == BORROWER_NFT, "Aloe: bad caller");
4. Next check passes: (a) correct permit selector, (b) to field corresponds to NFT1 borrower and matches msg.sender - this field is modified by attacker from the original user's transaction, but it passes, because signature of permit doesn't include to, so any to field will be accepted by Permit2, (c) signer is owner, which is the same both for NFT1 and NFT2, allowing attacker to reuse his signature but for a different NFT.
// Before calling `PERMIT2`, verify
// (a) correct function selector
// (b) `to` field is the Borrower (`msg.sender`)
// (c) correct signer address, i.e. [claimed Permit2 signer] == [user who owns the Borrower]
require(
bytes4(dataPermit2[:4]) == IPermit2.permitTransferFrom.selector &&
bytes20(dataPermit2[144:164]) == bytes20(msg.sender) &&
bytes20(dataPermit2[208:228]) == bytes20(data[:20])
);
5. Finally, the permit2 call transfers funds with permit from unsuspecting user to NFT1 (as described above, the to field is not part of the signature, so the attacker can reuse the same permit to transfer funds to a different NFT).
// Make calls
bool success;
(success, ) = address(PERMIT2).call(dataPermit2); // solhint-disable-line avoid-low-level-calls
if (!success) revert Permit2CallFailed();
6. Since attacker has full control over NFT1, he can immediately withdraw the funds he just stole.
Permit2Manager doesn't verify if the original modify caller has access to the NFT permit is supposed to transfer funds to, all checks are indirect.
y/src/managers/Permit2Manager.sol#L33-L73
Lack of direct check for NFT permit was given to allows to modify part of the permit which doesn't require signature and still pass all indirect checks, allowing to use permit with any NFT of the same owner.

Internal pre-conditions
User has several BorrowerNFTs and approves attacker for only one of the NFTs, then uses Permit2Manager for any of the other NFTs.
External pre-conditions
None
Attack Path
1. Attacker listens to the user transaction, takes permit data from it, changes to address to NFT he is approved to and front-runs the transaction with the same transaction of his own but for the NFT he's approved for. This allows to take funds from the user with this permit and deposit them into the NFT attacker controls.
2. Attacker immediately withdraws these funds from the NFT
Attacker can break BorrowerNFT approvals and take funds belonging to NFT the attacker is not approved for.

## Recommendation
Consider to require the owner to sign full permit data for Permit2Manager (including to field) in addition to permit itself.

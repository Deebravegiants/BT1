# [M] `safeTransferMany`

## Summary
Severity: Medium
Contest weight: 0.3606
Dataset id: 17356
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements two ERC721 tokens, BondNFT and GovNFT, each exposing a function named safeTransferMany that is intended to transfer multiple token IDs in a single call while performing the safety checks defined by ERC721. In reality the function calls the internal _transfer routine instead of _safeTransfer, so the required check that the recipient contract implements IERC721Receiver is omitted. The root cause is a mismatch between the function name and its implementation: the developer copied the single‑token safeTransferFrom logic but replaced the internal call with the non‑safe variant, possibly to avoid the receiver check, but left the name unchanged. An attacker or any user can exploit this by invoking safeTransferMany to send NFTs to a contract that does not implement onERC721Received. Because the transfer succeeds without a revert, the tokens become locked in a contract that has no way to acknowledge or forward them, effectively removing the assets from the owner's control. The impact is loss of ownership or inability to retrieve the NFTs, which may represent voting power, governance rights, or financial value. The vulnerability manifests whenever safeTransferMany is called with a recipient that is not an ERC721Receiver, i.e., any regular address or a contract without the required interface. Users, token holders, and the protocol that relies on the NFTs for governance are affected. The issue was discovered during a security audit when test cases expected a revert for transfers to a non‑receiver contract; the single‑token safeTransferFrom behaved correctly, but safeTransferMany did not revert, confirming the discrepancy between intent and behavior. Because the function name suggests safety, developers and auditors may overlook the missing check, especially if they rely on naming conventions rather than reviewing the internal call. The bug belongs to the class of “unsafe token transfer” or “missing receiver validation” bugs common in ERC721 implementations. From a user perspective the UI may show a successful transfer, but later the NFT no longer appears in the wallet and cannot be displayed, leading to confusion such as “my token disappeared” or “the transfer succeeded but I cannot see the NFT”. The expected behavior is that the contract reverts when the recipient does not implement IERC721Receiver; the actual behavior is that the transfer succeeds, violating the ERC721 safety guarantees and breaking accounting assumptions about token custody. The recommended remediation is to replace the internal _transfer call with _safeTransfer for each token ID, or to rename the function to reflect that it performs an unsafe transfer, thereby aligning implementation with intent and restoring the ERC721 safety checks.

## Proof of Concept
I’ve added the following tests to the `GovNFT` tests.

1st test will succeed (tx will revert) since `safeTransferFrom()` does actually use safe transfer.

2nd will fail (tx won’t revert), since `safeTransferMany()` doesn’t actually use a safe transfer.
    
    diff --git a/test/05.GovNFT.js b/test/05.GovNFT.js
    index 711a649..d927320 100644
    --- a/test/05.GovNFT.js
    +++ b/test/05.GovNFT.js
    @@ -98,6 +98,14 @@ describe("govnft", function () {
           expect(await govnft.pending(owner.getAddress(), StableToken.address)).to.equal(1500);
           expect(await govnft.pending(user.getAddress(), StableToken.address)).to.equal(500);
         });
    +
    +    it("Safe transfer to non ERC721Receiver", async function () {
    +      expect(govnft.connect(owner)['safeTransferFrom(address,address,uint256)'](owner.address,StableToken.address, 2)).to.be.revertedWith("ERC721: transfer to non ERC721Receiver implementer");
    +    });
    +    it("Safe transfer many  to non ERC721Receiver", async function () {
    +      await expect(govnft.connect(owner).safeTransferMany(StableToken.address, [2])).to.be.revertedWith("ERC721: transfer to non ERC721Receiver implementer");
    +    });
         it("Transferring an NFT with pending delisted rewards should not affect pending rewards", async function () {
           await govnft.connect(owner).safeTransferMany(user.getAddress(), [2,3]);
           expect(await govnft.balanceOf(owner.getAddress())).to.equal(0);

Output (I’ve shortened the output. following test will also fail, since the successful transfer will affect them):
    
          ✔ Safe transfer to contract
          1) Safe transfer many to contract
    
      11 passing (3s)
      1 failing
    
      1) govnft
           Reward system related functions
             Safe transfer many to contract:

          AssertionError: Expected transaction to be reverted
          + expected - actual

          -Transaction NOT reverted.
          +Transaction reverted.

## Recommendation
Call `_safeTransfer()` instead of `_transfer()`.

The Warden has shown a discrepancy between the intent of the code and the actual functionality when it comes to the `safeTransfer...` function.

Because this finding is reliant on understanding the intention of the Sponsor, and in this case they have confirmed, I believe that the finding is valid and of Medium Severity, because the function was intended to be using the safe checks, but wasn’t.

**[GainsGoblin (Tigris Trade) resolved](https://github.com/code-423n4/2022-12-tigris-findings/issues/356#issuecomment-1407533514):**

Mitigation: <https://github.com/code-423n4/2022-12-tigris/pull/2#issuecomment-1419175381>

We decided that we do not want transfers to check that the receiver is implementing IERC721Receiver, so we renamed the functions.

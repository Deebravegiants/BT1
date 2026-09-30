# [M] Contract `PhiNFT1155` can’t be paused

## Summary
Severity: Medium
Contest weight: 0.5420
Dataset id: 21870
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a faulty pausing mechanism in the PhiNFT1155 contract. The contract inherits from PausableUpgradeable but does not integrate the pause flag into the ERC1155 transfer logic, so when the owner calls pauseArtContract the internal paused state is set but the ERC1155 functions safeTransferFrom, safeBatchTransferFrom and internal _update are not guarded by the whenNotPaused modifier. As a result users can still move NFTs while the contract reports a paused status. The root cause is the use of the generic PausableUpgradeable base instead of ERC1155PausableUpgradeable and the missing override that combines supply tracking with the pause check. An attacker or any token holder can exploit this by calling safeTransferFrom after the contract has been paused, causing tokens to be transferred despite the expectation that transfers are frozen. The impact is that the intended security control – freezing token movement during emergencies, upgrades or disputes – is ineffective, allowing funds to be moved unexpectedly, breaking trust and potentially enabling theft or circumvention of governance decisions. The condition under which this occurs is any time the contract owner invokes the pause function; the UI may display a paused indicator, yet the transfer functions succeed without reverting. All participants who rely on the pause, including token owners, collectors, and the protocol that assumes assets are locked, are affected. The issue was discovered during an audit by adding a test that pauses the contract and then attempts a transfer, which succeeds. The bug is subtle because the pause flag is correctly stored and visible, so developers may assume the contract is secure, while the missing enforcement is not obvious from the code. To remediate, the contract should inherit from ERC1155PausableUpgradeable, which adds the required whenNotPaused check to token transfers, and override the internal _update function to combine the supply extension with the pausable extension, ensuring that any transfer while paused reverts. This aligns the implementation with the intended business logic that assets cannot be moved when the contract is paused.

## Proof of Concept
Drop this test to [PhiFactory.t.sol](https://github.com/code-423n4/2024-08-phi/blob/8c0985f7a10b231f916a51af5d506dd6b0c54120/test/PhiFactory.t.sol#L163) and execute via `forge test --match-test Kuprum`:

```solidity
function testKuprum_PhiNFT1155PauseNotWorking() public {
    _createArt(ART_ID_URL_STRING);
    uint256 artId = 1;
    bytes32 advanced_data = bytes32("1");
    bytes memory signData =
        abi.encode(expiresIn, participant, referrer, verifier, artId, block.chainid, advanced_data);
    bytes32 msgHash = keccak256(signData);
    bytes32 digest = ECDSA.toEthSignedMessageHash(msgHash);
    (uint8 v, bytes32 r, bytes32 s) = vm.sign(claimSignerPrivateKey, digest);
    if (v != 27) s = s | bytes32(uint256(1) << 255);
    bytes memory signature = abi.encodePacked(r, s);
    bytes memory data =
        abi.encode(1, participant, referrer, verifier, expiresIn, uint256(1), advanced_data, IMAGE_URL, signature);
    bytes memory dataCompressed = LibZip.cdCompress(data);
    uint256 totalMintFee = phiFactory.getArtMintFee(1, 1);

    vm.startPrank(participant, participant);
    phiFactory.claim{ value: totalMintFee }(dataCompressed);

    // referrer payout
    address artAddress = phiFactory.getArtAddress(1);
    assertEq(IERC1155(artAddress).balanceOf(participant, 1), 1, "participant erc1155 balance");
    
    // Everything up to here is from `test_claim_1155_with_ref`
    
    // Owner pauses the art contract
    vm.startPrank(owner);
    phiFactory.pauseArtContract(artAddress);

    // Users are still able to transfer NFTs despite the contract being paused
    assertEq(IERC1155(artAddress).balanceOf(user1, 1), 0, "user1 doesn't have any tokens");
    vm.startPrank(participant);
    IERC1155(artAddress).safeTransferFrom(participant, user1, 1, 1, hex"00");
    assertEq(IERC1155(artAddress).balanceOf(participant, 1), 0, "participant now has 0 tokens");
    assertEq(IERC1155(artAddress).balanceOf(user1, 1), 1, "user1 now has 1 token");
}
```

## Recommendation
We recommend to inherit from `ERC1155PausableUpgradeable` instead of `PausableUpgradeable`; this enforces the paused state on the NFT transfer functions. Apply the following diff to [PhiNFT1155.sol](https://github.com/code-423n4/2024-08-phi/blob/8c0985f7a10b231f916a51af5d506dd6b0c54120/src/art/PhiNFT1155.sol#L21-L31):

```diff
diff --git a/src/art/PhiNFT1155.sol b/src/art/PhiNFT1155.sol
index a280d05..258cb5a 100644
--- a/src/art/PhiNFT1155.sol
+++ b/src/art/PhiNFT1155.sol
@@ -8,7 +8,8 @@ import { Claimable } from "../abstract/Claimable.sol";
 import { ERC1155Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC1155/ERC1155Upgradeable.sol";
 import { ERC1155SupplyUpgradeable } from
     "@openzeppelin/contracts-upgradeable/token/ERC1155/extensions/ERC1155SupplyUpgradeable.sol";
- import { PausableUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/PausableUpgradeable.sol";
+ import { ERC1155PausableUpgradeable } from 
+    "@openzeppelin/contracts-upgradeable/token/ERC1155/extensions/ERC1155PausableUpgradeable.sol";
 import { ReentrancyGuardUpgradeable } from "@openzeppelin/contracts-upgradeable/utils/ReentrancyGuardUpgradeable.sol";
 import { Ownable2StepUpgradeable } from "@openzeppelin/contracts-upgradeable/access/Ownable2StepUpgradeable.sol";
 import { SafeTransferLib } from "solady/utils/SafeTransferLib.sol";
@@ -23,12 +24,21 @@ contract PhiNFT1155 is
     UUPSUpgradeable,
     ERC1155SupplyUpgradeable,
     ReentrancyGuardUpgradeable,
-    PausableUpgradeable,
+    ERC1155PausableUpgradeable,
     Ownable2StepUpgradeable,
     IPhiNFT1155,
     Claimable,
     CreatorRoyaltiesControl
 {
+    // The following functions are overrides required by Solidity.
+
+    function _update(address from, address to, uint256[] memory ids, uint256[] memory values)
+        internal
+        override(ERC1155PausableUpgradeable, ERC1155SupplyUpgradeable)
+    {
+        super._update(from, to, ids, values);
+    }
+
     /*//////////////////////////////////////////////////////////////
                                 USING
     //////////////////////////////////////////////////////////////*/
```

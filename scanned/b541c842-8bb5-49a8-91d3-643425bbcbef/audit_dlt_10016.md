# [?] Merge branch 'main' of github.com:morpho-labs/morpho-blue into fix/underflow

## Summary
Severity: Unknown
Chain: Morpho
Component: morpho-org/morpho-blue
Published: 2023-08-28
Source: https://github.com/morpho-org/morpho-blue/commit/e9bcbee816d601c2a63db22bf2b40dc9dddd3b1f
Type: security-commit

## Details
Merge branch 'main' of github.com:morpho-labs/morpho-blue into fix/underflow

## Patch
### LICENSE
```diff
@@ -0,0 +1,103 @@
+Business Source License 1.1
+
+License text copyright (c) 2017 MariaDB Corporation Ab, All Rights Reserved.
+"Business Source License" is a trademark of MariaDB Corporation Ab.
+
+-----------------------------------------------------------------------------
+
+Parameters
+
+Licensor:             Morpho Association
+
+Licensed Work:        Morpho Blue Core
+                      The Licensed Work is (c) 2023 Morpho Association
+
+Additional Use Grant: Any uses listed and defined at
+                      morpho-blue-core-license-grants.morpho.eth
+
+Change Date:          The earlier of (i) 2026-01-01, or (ii) a date specified
+                      at morpho-blue-core-license-date.morpho.eth, or (iii)
+                      upon the activation of the setFee function of the
+                      Licensed Work’s applicable protocol smart contracts
+                      deployed for production use.
+
+Change License:       GNU General Public License v2.0 or later
+
+-----------------------------------------------------------------------------
+
+Terms
+
+The Licensor hereby grants you the right to copy, modify, create derivative
+works, redistribute, and make non-production use of the Licensed Work. The
+Licensor may make an Additional Use Grant, above, permitting limited
+production use.
+
+Effective on the Change Date, or the fourth anniversary of the first publicly
+available distribution of a specific version of the Licensed Work under this
+License, whichever comes first, the Licensor hereby grants you rights under
+the terms of the Change License, and the rights granted in the paragraph
+above terminate.
+
+If your use of the Licensed Work does not comply with the requirements
+currently in effect as described in this License, you must purchase a
+commercial license from the Licensor, its affiliated entities, or authorized
+resellers, or you must refrain from using the Licensed Work.
+
+All copies of the original and modified Licensed Work, and derivative works
+of the Licensed Work, are subject to this License. This License applies
+separately for each version of the Licensed Work and the Change Date may vary
+for each version of the Licensed Work released by Licensor.
+
+You must conspicuously display this License on each original or modified copy
+of the Licensed Work. If you receive the Licensed Work in original or
+modified form from a third party, the terms and conditions set forth in this
+License apply to your use of that work.
+
+Any use of the Licensed Work in violation of this License will automatically
+terminate your rights under this License for the current and all other
+versions of the Licensed Work.
+
+This License does not grant you any right in any trademark or logo of
+Licensor or its affiliates (provided that you may use a trademark or logo of
+Licensor as expressly required by this License).
+
+TO THE EXTENT PERMITTED BY APPLICABLE LAW, THE LICENSED WORK IS PROVIDED ON
+AN "AS IS" BASIS. LICENSOR HEREBY DISCLAIMS ALL WARRANTIES AND CONDITIONS,
+EXPRESS OR IMPLIED, INCLUDING (WITHOUT LIMITATION) WARRANTIES OF
+MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND
+TITLE.
+
+MariaDB hereby grants you permission to use this License’s text to license
+your works, and to refer to it using the trademark "Business Source License",
+as long as you comply with the Covenants of Licensor below.
+
+-----------------------------------------------------------------------------
+
+Covenants of Licensor
+
+In consideration of the right to use this License’s text and the "Business
+Source License" name and trademark, Licensor covenants to MariaDB, and to all
+other recipients of the licensed work to be provided by Licensor:
+
+1. To specify as the Change License the GPL Version 2.0 or any later version,
+   or a license that is compatible with GPL Version 2.0 or a later version,
+   where "compatible" means that software provided under the Change License can
+   be included in a program with software provided under GPL Version 2.0 or a
+   later version. Licensor may specify additional Change Licenses without
+   limitation.
+
+2. To either: (a) specify an additional grant of rights to use that does not
+   impose any additional restriction on the right granted in this License, as
+   the Additional Use Grant; or (b) insert the text "None".
+
+3. To specify a Change Date.
+
+4. Not to modify this License in any other way.
+
+-----------------------------------------------------------------------------
+
+Notice
+
+The Business Source License (this document, or the "License") is not an Open
+Source license. However, the Licensed Work will eventually be made available
+under an Open Source License, as stated in this License.
```

### README.md
```diff
@@ -0,0 +1,11 @@
+# Morpho Blue
+
+## Licensing
+
+The primary license for Morpho Blue is the Business Source License 1.1 (`BUSL-1.1`), see [`LICENSE`](./LICENSE). However, some files are dual licensed under `GPL-2.0-or-later`.
+
+All files in the following folders can also be licensed under `GPL-2.0-or-later` (as indicated in their SPDX headers):
+- `src/interfaces`, see [`src/interfaces/LICENSE`](./src/interfaces/LICENSE)
+- `src/libraries`, see [`src/libraries/LICENSE`](./src/libaries/LICENSE)
+- `src/mocks`, see [`src/mocks/LICENSE`](./src/mocks/LICENSE)
+- `test`, see [`test/LICENSE`](./test/LICENSE)
```

### package.json
```diff
@@ -1,4 +1,8 @@
 {
+  "name": "morpho-blue",
+  "description": "Morpho Blue Protocol",
+  "license": "BUSL-1.1",
+  "version": "1.0.0",
   "scripts": {
     "postinstall": "husky install && forge install",
     "build:forge": "FOUNDRY_PROFILE=build forge build",
```

### src/Morpho.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: BUSL-1.1
 pragma solidity 0.8.19;
 
 import {Id, IMorpho, MarketParams, Position, Market, Authorization, Signature} from "./interfaces/IMorpho.sol";
@@ -459,7 +459,7 @@ contract Morpho is IMorpho {
             if (market[id].fee != 0) {
                 uint256 feeAmount = interest.wMulDown(market[id].fee);
                 // The fee amount is subtracted from the total supply in this calculation to compensate for the fact
-                // that total supply is already updated.
+                // that total supply is already increased by the full interest (including the fee amount).
                 feeShares =
                     feeAmount.toSharesDown(market[id].totalSupplyAssets - feeAmount, market[id].totalSupplyShares);
                 position[id][feeRecipient].supplyShares += feeShares;
```

### src/interfaces/IERC20.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity >=0.6.2;
 
 /// @title IERC20
```

### src/interfaces/IIrm.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity >=0.6.2;
 
 import {MarketParams, Market} from "./IMorpho.sol";
```

### src/interfaces/IMorpho.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity >=0.8.8;
 
 type Id is bytes32;
@@ -65,10 +65,23 @@ interface IMorpho {
     function feeRecipient() external view returns (address);
 
     /// @notice The state of the position of `user` on the market corresponding to `id`.
-    function position(Id id, address user) external view returns (uint256, uint128, uint128);
+    function position(Id id, address user)
+        external
+        view
+        returns (uint256 supplyShares, uint128 borrowShares, uint128 collateral);
 
     /// @notice The state of the market corresponding to `id`.
-    function market(Id id) external view returns (uint128, uint128, uint128, uint128, uint128, uint128);
+    function market(Id id)
+        external
+        view
+        returns (
+            uint128 totalSupplyAssets,
+            uint128 totalSupplyShares,
+            uint128 totalBorrowAssets,
+            uint128 totalBorrowShares,
+            uint128 lastUpdate,
+            uint128 fee
+        );
 
     /// @notice Whether the `irm` is enabled.
     function isIrmEnabled(address irm) external view returns (bool);
@@ -96,11 +109,11 @@ interface IMorpho {
     /// @dev Warning: The owner can be set to the zero address.
     function setOwner(address newOwner) external;
 
-    /// @notice Enables `irm` as possible IRM for market creation.
+    /// @notice Enables `irm` as a possible IRM for market creation.
     /// @dev Warning: It is not possible to disable an IRM.
     function enableIrm(address irm) external;
 
-    /// @notice Enables `lltv` as possible LLTV for market creation.
+    /// @notice Enables `lltv` as a possible LLTV for market creation.
     /// @dev Warning: It is not possible to disable a LLTV.
     function enableLltv(uint256 lltv) external;
 
@@ -115,6 +128,26 @@ interface IMorpho {
     function setFeeRecipient(address newFeeRecipient) external;
 
     /// @notice Creates the market `marketParams`.
+    /// @dev Here is the list of assumptions on the market's dependencies (tokens, IRM and oracle) that guarantees
+    /// Morpho behaves as expected:
+    /// - The token should be ERC-20 compliant, except that it can omit return values on `transfer` and `transferFrom`.
+    /// - The token balance of Morpho should only decrease on `transfer` and `transferFrom`. In particular, tokens with
+    /// burn functions are not supported.
+    /// - The token should not re-enter Morpho on `transfer` nor `transferFrom`.
+    /// - The token balance of the sender (resp. receiver) should decrease (resp. increase) by exactly the given amount
+    /// on `transfer` and `transferFrom`. In particular, tokens with fees on transfer are not supported.
+    /// - The IRM should not re-enter Morpho.
+    /// @dev Here is a list of properties on the market's dependencies that could break Morpho's liveness properties:
+    /// - The token can revert on `transfer` and `transferFrom` for a reason other than an approval or balance issue.
+    /// - A very high amount of assets (~1e35) supplied or borrowed can make the computation of `toSharesUp` and
+    /// `toSharesDown` overflow.
+    /// - The IRM can revert on `borrowRate`.
+    /// - A very high borrow rate returned by the IRM can make the computation of `interest` in `_accrueInterest`
+    /// overflow.
+    /// - The oracle can revert on `price`. Note that this can be used to prevent `borrow`, `withdrawCollateral` and
+    /// `liquidate` from being used under certain market conditions.
+    /// - A very high price returned by the oracle can make the computation of `maxBorrow` in `_isHealthy` overflow, or
+    /// the computation of `assetsRepaid` in `liquidate` overflow.
     function createMarket(MarketParams memory marketParams) external;
 
     /// @notice Supplies `assets` or `shares` on behalf of `onBehalf`, optionally calling back the caller's
@@ -126,7 +159,7 @@ interface IMorpho {
     /// @param marketParams The market to supply assets to.
     /// @param assets The amount of assets to supply.
     /// @param shares The amount of shares to mint.
-    /// @param onBehalf The address that will receive the position.
+    /// @param onBehalf The address that will own the increased supply position.
     /// @param data Arbitrary data to pass to the `onMorphoSupply` callback. Pass empty data if not needed.
     /// @return assetsSupplied The amount of assets supplied.
     /// @return sharesSupplied The amount of shares minted.
@@ -145,7 +178,7 @@ interface IMorpho {
     /// @param marketParams The market to withdraw assets from.
     /// @param assets The amount of assets to withdraw.
     /// @param shares The amount of shares to burn.
-    /// @param onBehalf The address of the owner of the withdrawn assets.
+    /// @param onBehalf The address of the owner of the supply position.
     /// @param receiver The address that will receive the withdrawn assets.
     /// @return assetsWithdrawn The amount of assets withdrawn.
     /// @return sharesWithdrawn The amount of shares burned.
@@ -166,8 +199,8 @@ interface IMorpho {
     /// @param marketParams The market to borrow assets from.
     /// @param assets The amount of assets to borrow.
     /// @param shares The amount of shares to mint.
-    /// @param onBehalf The address of the owner of the debt.
-    /// @param receiver The address that will receive the debt.
+    /// @param onBehalf The address that will own the increased borrow position.
+    /// @param receiver The address that will receive the borrowed assets.
     /// @return assetsBorrowed The amount of assets borrowed.
     /// @return sharesBorrowed The amount of shares minted.
     function borrow(
@@ -185,7 +218,7 @@ interface IMorpho {
     /// @param marketParams The market to repay assets to.
     /// @param assets The amount of assets to repay.
     /// @param shares The amount of shares to burn.
-    /// @param onBehalf The address of the owner of the debt.
+    /// @param onBehalf The address of the owner of the debt position.
     /// @param data Arbitrary data to pass to the `onMorphoRepay` callback. Pass empty data if not needed.
     /// @return assetsRepaid The amount of assets repaid.
     /// @return sharesRepaid The amount of shares burned.
@@ -203,7 +236,7 @@ interface IMorpho {
     /// @dev Supplying a large amount can revert for overflow.
     /// @param marketParams The market to supply collateral to.
     /// @param assets The amount of collateral to supply.
-    /// @param onBehalf The address that will receive the collateral.
+    /// @param onBehalf The address that will own the increased collateral position.
     /// @param data Arbitrary data to pass to the `onMorphoSupplyCollateral` callback. Pass empty data if not needed.
     function supplyCollateral(MarketParams memory marketParams, uint256 assets, address onBehalf, bytes memory data)
         external;
@@ -213,15 +246,15 @@ interface IMorpho {
     /// @dev Withdrawing an amount corresponding to more collateral than supplied will revert for underflow.
     /// @param marketParams The market to withdraw collateral from.
     /// @param assets The amount of collateral to withdraw.
-    /// @param onBehalf The address of the owner of the collateral.
-    /// @param receiver The address that will receive the withdrawn collateral.
+    /// @param onBehalf The address of the owner of the collateral position.
+    /// @param receiver The address that will receive the collateral assets.
     function withdrawCollateral(MarketParams memory marketParams, uint256 assets, address onBehalf, address receiver)
         external;
 
-    /// @notice Liquidates the given `repaidShares` of debt asset or seize the given `seized` of collateral on the given
-    /// `market` of the given `borrower`'s position, optionally calling back the caller's `onMorphoLiquidate` function
-    /// with the given `data`.
-    /// @dev Either `seized` or `repaidShares` should be zero.
+    /// @notice Liquidates the given `repaidShares` of debt asset or seize the given `seizedAssets` of collateral on the
+    /// given market `marketParams` of the given `borrower`'s position, optionally calling back the caller's
+    /// `onMorphoLiquidate` function with the given `data`.
+    /// @dev Either `seizedAssets` or `repaidShares` should be zero.
     /// @dev Seizing more than the collateral balance will underflow and revert without any error message.
     /// @dev Repaying more than the borrow balance will underflow and revert without any error message.
     /// @param marketParams The market of the position.
@@ -259,5 +292,5 @@ interface IMorpho {
     function setAuthorizationWithSig(Authorization calldata authorization, Signature calldata signature) external;
 
     /// @notice Returns the data stored on the different `slots`.
-    function extSloads(bytes32[] memory slots) external view returns (bytes32[] memory res);
+    function extSloads(bytes32[] memory slots) external view returns (bytes32[] memory);
 }
```

### src/interfaces/IMorphoCallbacks.sol
```diff
@@ -1,14 +1,14 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity >=0.6.2;
 
 /// @title IMorphoLiquidateCallback
 /// @notice Interface that liquidators willing to use `liquidate`'s callback must implement.
 interface IMorphoLiquidateCallback {
     /// @notice Callback called when a liquidation occurs.
     /// @dev The callback is called only if data is not empty.
-    /// @param assets The amount of repaid assets.
+    /// @param repaidAssets The amount of repaid assets.
     /// @param data Arbitrary data passed to the `liquidate` function.
-    function onMorphoLiquidate(uint256 assets, bytes calldata data) external;
+    function onMorphoLiquidate(uint256 repaidAssets, bytes calldata data) external;
 }
 
 /// @title IMorphoRepayCallback
```

### src/interfaces/IOracle.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity >=0.6.2;
 
 /// @title IOracle
```

### src/interfaces/LICENSE
```diff
@@ -0,0 +1,389 @@
+This software is available under your choice of the GNU General Public
+License, version 2 or later, or the Business Source License, as set
+forth below.
+
+                    GNU GENERAL PUBLIC LICENSE
+                       Version 2, June 1991
+
+ Copyright (C) 1989, 1991 Free Software Foundation, Inc.,
+ 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
+ Everyone is permitted to copy and distribute verbatim copies
+ of this license document, but changing it is not allowed.
+
+                            Preamble
+
+  The licenses for most software are designed to take away your
+freedom to share and change it.  By contrast, the GNU General Public
+License is intended to guarantee your freedom to share and change free
+software--to make sure the software is free for all its users.  This
+General Public License applies to most of the Free Software
+Foundation's software and to any other program whose authors commit to
+using it.  (Some other Free Software Foundation software is covered by
+the GNU Lesser General Public License instead.)  You can apply it to
+your programs, too.
+
+  When we speak of free software, we are referring to freedom, not
+price.  Our General Public Licenses are designed to make sure that you
+have the freedom to distribute copies of free software (and charge for
+this service if you wish), that you receive source code or can get it
+if you want it, that you can change the software or use pieces of it
+in new free programs; and that you know you can do these things.
+
+  To protect your rights, we need to make restrictions that forbid
+anyone to deny you these rights or to ask you to surrender the rights.
+These restrictions translate to certain responsibilities for you if you
+distribute copies of the software, or if you modify it.
+
+  For example, if you distribute copies of such a program, whether
+gratis or for a fee, you must give the recipients all the rights that
+you have.  You must make sure that they, too, receive or can get the
+source code.  And you must show them these terms so they know their
+rights.
+
+  We protect your rights with two steps: (1) copyright the software, and
+(2) offer you this license which gives you legal permission to copy,
+distribute and/or modify the software.
+
+  Also, for each author's protection and ours, we want to make certain
+that everyone understands that there is no warranty for this free
+software.  If the software is modified by someone else and passed on, we
+want its recipients to know that what they have is not the original, so
+that any problems introduced by others will not reflect on the original
+authors' reputations.
+
+  Finally, any free program is threatened constantly by software
+patents.  We wish to avoid the danger that redistributors of a free
+program will individually obtain patent licenses, in effect making the
+program proprietary.  To prevent this, we have made it clear that any
+patent must be licensed for everyone's free use or not licensed at all.
+
+  The precise terms and conditions for copying, distribution and
+modification follow.
+
+                    GNU GENERAL PUBLIC LICENSE
+   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
+
+  0. This License applies to any program or other work which contains
+a notice placed by the copyright holder saying it may be distributed
+under the terms of this General Public License.  The "Program", below,
+refers to any such program or work, and a "work based on the Program"
+means either the Program or any derivative work under copyright law:
+that is to say, a work containing the Program or a portion of it,
+either verbatim or with modifications and/or translated into another
+language.  (Hereinafter, translation is included without limitation in
+the term "modification".)  Each licensee is addressed as "you".
+
+Activities other than copying, distribution and modification are not
+covered by this License; they are outside its scope.  The act of
+running the Program is not restricted, and the output from the Program
+is covered only if its contents constitute a work based on the
+Program (independent of having been made by running the Program).
+Whether that is true depends on what the Program does.
+
+  1. You may copy and distribute verbatim copies of the Program's
+source code as you receive it, in any medium, provided that you
+conspicuously and appropriately publish on each copy an appropriate
+copyright notice and disclaimer of warranty; keep intact all the
+notices that refer to this License and to the absence of any warranty;
+and give any other recipients of the Program a copy of this License
+along with the Program.
+
+You may charge a fee for the physical act of transferring a copy, and
+you may at your option offer warranty protection in exchange for a fee.
+
+  2. You may modify your copy or copies of the Program or any portion
+of it, thus forming a work based on the Program, and copy and
+distribute such modifications or work under the terms of Section 1
+above, provided that you also meet all of these conditions:
+
+    a) You must cause the modified files to carry prominent notices
+    stating that you changed the files and the date of any change.
+
+    b) You must cause any work that you distribute or publish, that in
+    whole or in part contains or is derived from the Program or any
+    part thereof, to be licensed as a whole at no charge to all third
+    parties under the terms of this License.
+
+    c) If the modified program normally reads commands interactively
+    when run, you must cause it, when started running for such
+    interactive use in the most ordinary way, to print or display an
+    announcement including an appropriate copyright notice and a
+    notice that there is no warranty (or else, saying that you provide
+    a warranty) and that users may redistribute the program under
+    these conditions, and telling the user how to view a copy of this
+    License.  (Exception: if the Program itself is interactive but
+    does not normally print such an announcement, your work based on
+    the Program is not required to print an announcement.)
+
+These requirements apply to the modified work as a whole.  If
+identifiable sections of that work are not derived from the Program,
+and can be reasonably considered independent and separate works in
+themselves, then this License, and its terms, do not apply to those
+sections when you distribute them as separate works.  But when you
+distribute the same sections as part of a whole which is a work based
+on the Program, the distribution of the whole must be on the terms of
+this License, whose permissions for other licensees extend to the
+entire whole, and thus to each and every part regardless of who wrote it.
+
+Thus, it is not the intent of this section to claim rights or contest
+your rights to work written entirely by you; rather, the intent is to
+exercise the right to control the distribution of derivative or
+collective works based on the Program.
+
+In addition, mere aggregation of another work not based on the Program
+with the Program (or with a work based on the Program) on a volume of
+a storage or distribution medium does not bring the other work under
+the scope of this License.
+
+  3. You may copy and distribute the Program (or a work based on it,
+under Section 2) in object code or executable form under the terms of
+Sections 1 and 2 above provided that you also do one of the following:
+
+    a) Accompany it with the complete corresponding machine-readable
+    source code, which must be distributed under the terms of Sections
+    1 and 2 above on a medium customarily used for software interchange; or,
+
+    b) Accompany it with a written offer, valid for at least three
+    years, to give any third party, for a charge no more than your
+    cost of physically performing source distribution, a complete
+    machine-readable copy of the corresponding source code, to be
+    distributed under the terms of Sections 1 and 2 above on a medium
+    customarily used for software interchange; or,
+
+    c) Accompany it with the information you received as to the offer
+    to distribute corresponding source code.  (This alternative is
+    allowed only for noncommercial distribution and only if you
+    received the program in object code or executable form with such
+    an offer, in accord with Subsection b above.)
+
+The source code for a work means the preferred form of the work for
+making modifications to it.  For an executable work, complete source
+code means all the source code for all modules it contains, plus any
+associated interface definition files, plus the scripts used to
+control compilation and installation of the executable.  However, as a
+special exception, the source code distributed need not include
+anything that is normally distributed (in either source or binary
+form) with the major components (compiler, kernel, and so on) of the
+operating system on which the executable runs, unless that component
+itself accompanies the executable.
+
+If distribution of executable or object code is made by offering
+access to copy from a designated place, then offering equivalent
+access to copy the source code from the same place counts as
+distribution of the source code, even though third parties are not
+compelled to copy the source along with the object code.
+
+  4. You may not copy, modify, sublicense, or distribute the Program
+except as expressly provided under this License.  Any attempt
+otherwise to copy, modify, sublicense or distribute the Program is
+void, and will automatically terminate your rights under this License.
+However, parties who have received copies, or rights, from you under
+this License will not have their licenses terminated so long as such
+parties remain in full compliance.
+
+  5. You are not required to accept this License, since you have not
+signed it.  However, nothing else grants you permission to modify or
+distribute the Program or its derivative works.  These actions are
+prohibited by law if you do not accept this License.  Therefore, by
+modifying or distributing the Program (or any work based on the
+Program), you indicate your acceptance of this License to do so, and
+all its terms and conditions for copying, distributing or modifying
+the Program or works based on it.
+
+  6. Each time you redistribute the Program (or any work based on the
+Program), the recipient automatically receives a license from the
+original licensor to copy, distribute or modify the Program subject to
+these terms and conditions.  You may not impose any further
+restrictions on the recipients' exercise of the rights granted herein.
+You are not responsible for enforcing compliance by third parties to
+this License.
+
+  7. If, as a consequence of a court judgment or allegation of patent
+infringement or for any other reason (not limited to patent issues),
+conditions are imposed on you (whether by court order, agreement or
+otherwise) that contradict the conditions of this License, they do not
+excuse you from the conditions of this License.  If you cannot
+distribute so as to satisfy simultaneously your obligations under this
+License and any other pertinent obligations, then as a consequence you
+may not distribute the Program at all.  For example, if a patent
+license would not permit royalty-free redistribution of the Program by
+all those who receive copies directly or indirectly through you, then
+the only way you could satisfy both it and this License would be to
+refrain entirely from distribution of the Program.
+
+If any portion of this section is held invalid or unenforceable under
+any particular circumstance, the balance of the section is intended to
+apply and the section as a whole is intended to apply in other
+circumstances.
+
+It is not the purpose of this section to induce you to infringe any
+patents or other property right claims or to contest validity of any
+such claims; this section has the sole purpose of protecting the
+integrity of the free software distribution system, which is
+implemented by public license practices.  Many people have made
+generous contributions to the wide range of software distributed
+through that system in reliance on consistent application of that
+system; it is up to the author/donor to decide if he or she is willing
+to distribute software through any other system and a licensee cannot
+impose that choice.
+
+This section is intended to make thoroughly clear what is believed to
+be a consequence of the rest of this License.
+
+  8. If the distribution and/or use of the Program is restricted in
+certain countries either by patents or by copyrighted interfaces, the
+original copyright holder who places the Program under this License
+may add an explicit geographical distribution limitation excluding
+those countries, so that distribution is permitted only in or among
+countries not thus excluded.  In such case, this License incorporates
+the limitation as if written in the body of this License.
+
+  9. The Free Software Foundation may publish revised and/or new versions
+of the General Public License from time to time.  Such new versions will
+be similar in spirit to the present version, but may differ in detail to
+address new problems or concerns.
+
+Each version is given a distinguishing version number.  If the Program
+specifies a version number of this License which applies to it and "any
+later version", you have the option of following the terms and conditions
+either of that version or of any later version published by the Free
+Software Foundation.  If the Program does not specify a version number of
+this License, you may choose any version ever published by the Free Software
+Foundation.
+
+  10. If you wish to incorporate parts of the Program into other free
+programs whose distribution conditions are different, write to the author
+to ask for permission.  For software which is copyrighted by the Free
+Software Foundation, write to the Free Software Foundation; we sometimes
+make exceptions for this.  Our decision will be guided by the two goals
+of preserving the free status of all derivatives of our free software and
+of promoting the sharing and reuse of software generally.
+
+                            NO WARRANTY
+
+  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
+FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
+OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
+PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
+OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
+MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
+TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
+PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
+REPAIR OR CORRECTION.
+
+  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
+WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
+REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
+INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
+OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
+TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
+YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
+PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
+POSSIBILITY OF SUCH DAMAGES.
+
+                     END OF TERMS AND CONDITIONS
+
+
+Business Source License 1.1
+
+License text copyright (c) 2017 MariaDB Corporation Ab, All Rights Reserved.
+"Business Source License" is a trademark of MariaDB Corporation Ab.
+
+-----------------------------------------------------------------------------
+
+Parameters
+
+Licensor:             Morpho Association
+
+Licensed Work:        Morpho Blue Core
+                      The Licensed Work is (c) 2023 Morpho Association
+
+Additional Use Grant: Any uses listed and defined at
+                      morpho-blue-core-license-grants.morpho.eth
+
+Change Date:          The earlier of (i) 2026-01-01, or (ii) a date specified
+                      at morpho-blue-core-license-date.morpho.eth, or (iii)
+                      upon the activation of the setFee function of the
+                      Licensed Work’s applicable protocol smart contracts
+                      deployed for production use.
+
+Change License:       GNU General Public License v2.0 or later
+
+-----------------------------------------------------------------------------
+
+Terms
+
+The Licensor hereby grants you the right to copy, modify, create derivative
+works, redistribute, and make non-production use of the Licensed Work. The
+Licensor may make an Additional Use Grant, above, permitting limited
+production use.
+
+Effective on the Change Date, or the fourth anniversary of the first publicly
+available distribution of a specific version of the Licensed Work under this
+License, whichever comes first, the Licensor hereby grants you rights under
+the terms of the Change License, and the rights granted in the paragraph
+above terminate.
+
+If your use of the Licensed Work does not comply with the requirements
+currently in effect as described in this License, you must purchase a
+commercial license from the Licensor, its affiliated entities, or authorized
+resellers, or you must refrain from using the Licensed Work.
+
+All copies of the original and modified Licensed Work, and derivative works
+of the Licensed Work, are subject to this License. This License applies
+separately for each version of the Licensed Work and the Change Date may vary
+for each version of the Licensed Work released by Licensor.
+
+You must conspicuously display this License on each original or modified copy
+of the Licensed Work. If you receive the Licensed Work in original or
+modified form from a third party, the terms and conditions set forth in this
+License apply to your use of that work.
+
+Any use of the Licensed Work in violation of this License will automatically
+terminate your rights under this License for the current and all other
+versions of the Licensed Work.
+
+This License does not grant you any right in any trademark or logo of
+Licensor or its affiliates (provided that you may use a trademark or logo of
+Licensor as expressly required by this License).
+
+TO THE EXTENT PERMITTED BY APPLICABLE LAW, THE LICENSED WORK IS PROVIDED ON
+AN "AS IS" BASIS. LICENSOR HEREBY DISCLAIMS ALL WARRANTIES AND CONDITIONS,
+EXPRESS OR IMPLIED, INCLUDING (WITHOUT LIMITATION) WARRANTIES OF
+MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT, AND
+TITLE.
+
+MariaDB hereby grants you permission to use this License’s text to license
+your works, and to refer to it using the trademark "Business Source License",
+as long as you comply with the Covenants of Licensor below.
+
+-----------------------------------------------------------------------------
+
+Covenants of Licensor
+
+In consideration of the right to use this License’s text and the "Business
+Source License" name and trademark, Licensor covenants to MariaDB, and to all
+other recipients of the licensed work to be provided by Licensor:
+
+1. To specify as the Change License the GPL Version 2.0 or any later version,
+   or a license that is compatible with GPL Version 2.0 or a later version,
+   where "compatible" means that software provided under the Change License can
+   be included in a program with software provided under GPL Version 2.0 or a
+   later version. Licensor may specify additional Change Licenses without
+   limitation.
+
+2. To either: (a) specify an additional grant of rights to use that does not
+   impose any additional restriction on the right granted in this License, as
+   the Additional Use Grant; or (b) insert the text "None".
+
+3. To specify a Change Date.
+
+4. Not to modify this License in any other way.
+
+-----------------------------------------------------------------------------
+
+Notice
+
+The Business Source License (this document, or the "License") is not an Open
+Source license. However, the Licensed Work will eventually be made available
+under an Open Source License, as stated in this License.
```

### src/libraries/ConstantsLib.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity ^0.8.0;
 
 /// @dev The maximum fee a market can have (25%).
```

### src/libraries/ErrorsLib.sol
```diff
@@ -1,4 +1,4 @@
-// SPDX-License-Identifier: UNLICENSED
+// SPDX-License-Identifier: GPL-2.0-or-later
 pragma solidity ^0.8.0;
 
 /// @title ErrorsLib
```

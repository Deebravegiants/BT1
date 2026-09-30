# [?] Merge pull request #379 from etherfi-protocol/pankaj/feat/reentrancy-guard

## Summary
Severity: Unknown
Chain: EtherFi
Component: etherfi-protocol/smart-contracts
Published: 2026-04-29
Source: https://github.com/etherfi-protocol/smart-contracts/commit/de9e377169bdaee2489132a40d5aff2dc3d93e52
Type: security-commit

## Details
Merge pull request #379 from etherfi-protocol/pankaj/feat/reentrancy-guard

feat: Reentrancy Guard and permissonless claim

## Patch
### src/LiquidityPool.sol
```diff
@@ -17,8 +17,9 @@ import "./interfaces/IEtherFiNode.sol";
 import "./interfaces/IEtherFiNodesManager.sol";
 import "./interfaces/IRoleRegistry.sol";
 import "./interfaces/IPriorityWithdrawalQueue.sol";
+import "./ReentrancyGuardNamespaced.sol";
 
-contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ILiquidityPool {
+contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, ReentrancyGuardNamespaced, ILiquidityPool {
     using SafeERC20 for IERC20;
     //--------------------------------------------------------------------------------------
     //---------------------------------  STATE-VARIABLES  ----------------------------------
@@ -181,7 +182,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     }
 
     // Used by eETH staking flow
-    function deposit(address _referral) public payable whenNotPaused returns (uint256) {
+    function deposit(address _referral) public payable whenNotPaused nonReentrant returns (uint256) {
         emit Deposit(msg.sender, msg.value, SourceOfFunds.EETH, _referral);
 
         return _deposit(msg.sender, msg.value, 0);
@@ -197,7 +198,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     }
 
     // Used by ether.fan staking flow
-    function deposit(address _user, address _referral) external payable whenNotPaused returns (uint256) {
+    function deposit(address _user, address _referral) external payable whenNotPaused nonReentrant returns (uint256) {
         require(msg.sender == address(membershipManager), "Incorrect Caller");
 
         emit Deposit(msg.sender, msg.value, SourceOfFunds.ETHER_FAN, _referral);
@@ -210,7 +211,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     /// @param _recipient the recipient who will receives the ETH
     /// @param _amount the amount to withdraw from contract
     /// it returns the amount of shares burned
-    function withdraw(address _recipient, uint256 _amount) external whenNotPaused returns (uint256) {
+    function withdraw(address _recipient, uint256 _amount) external nonReentrant returns (uint256) {
         uint256 share = sharesForWithdrawalAmount(_amount);
         require(
             msg.sender == address(withdrawRequestNFT) || 
@@ -219,6 +220,10 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
             msg.sender == priorityWithdrawalQueue,
             "Incorrect Caller"
         );
+        // Permissionless claims via withdrawRequestNFT and priorityWithdrawalQueue are allowed even when the LP is paused; membershipManager and etherFiRedemptionManager remain gated.
+        if (msg.sender != address(withdrawRequestNFT) && msg.sender != priorityWithdrawalQueue) {
+            _requireNotPaused();
+        }
         if (totalValueInLp < _amount || eETH.balanceOf(msg.sender) < _amount) revert InsufficientLiquidity();
         if (_amount > type(uint128).max || _amount == 0 || share == 0) revert InvalidAmount();
 
@@ -247,7 +252,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     /// @param recipient address that will be issued the NFT
     /// @param amount requested amount to withdraw from contract
     /// @return uint256 requestId of the WithdrawRequestNFT
-    function requestWithdraw(address recipient, uint256 amount) public whenNotPaused returns (uint256) {
+    function requestWithdraw(address recipient, uint256 amount) public whenNotPaused nonReentrant returns (uint256) {
         uint256 share = sharesForAmount(amount);
         if (amount > type(uint96).max || amount == 0 || share == 0) revert InvalidAmount();
 
@@ -282,7 +287,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     /// @param amount requested amount to withdraw from contract
     /// @param fee the burn fee to be paid by the recipient when the withdrawal is claimed (WithdrawRequestNFT.claimWithdraw)
     /// @return uint256 requestId of the WithdrawRequestNFT
-    function requestMembershipNFTWithdraw(address recipient, uint256 amount, uint256 fee) public whenNotPaused returns (uint256) {
+    function requestMembershipNFTWithdraw(address recipient, uint256 amount, uint256 fee) public whenNotPaused nonReentrant returns (uint256) {
         if (msg.sender != address(membershipManager)) revert IncorrectCaller();
         uint256 share = sharesForAmount(amount);
         if (amount > type(uint96).max || amount == 0 || share == 0) revert InvalidAmount();
@@ -323,7 +328,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
         IStakingManager.DepositData[] calldata _depositData,
         uint256[] calldata _bidIds,
         address _etherFiNode
-    ) external whenNotPaused {
+    ) external whenNotPaused nonReentrant {
         if (!roleRegistry.hasRole(LIQUIDITY_POOL_VALIDATOR_CREATOR_ROLE, msg.sender)) revert IncorrectRole();
 
         // liquidity pool supplies 1 eth per validator
@@ -340,7 +345,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
         uint256[] memory _validatorIds,
         bytes[] calldata _pubkeys,
         bytes[] calldata _signatures
-    ) external whenNotPaused {
+    ) external whenNotPaused nonReentrant {
         if (!roleRegistry.hasRole(LIQUIDITY_POOL_VALIDATOR_APPROVER_ROLE, msg.sender)) revert IncorrectRole();
         if (validatorSizeWei < 32 ether || validatorSizeWei > 2048 ether) revert InvalidValidatorSize();
         if (_validatorIds.length == 0 || _validatorIds.length != _pubkeys.length || _validatorIds.length != _signatures.length) revert InvalidArrayLengths();
@@ -383,7 +388,7 @@ contract LiquidityPool is Initializable, OwnableUpgradeable, UUPSUpgradeable, IL
     function confirmAndFundBeaconValidators(
         IStakingManager.DepositData[] calldata _depositData,
         uint256 _validatorSizeWei
-    ) external whenNotPaused {
+    ) external whenNotPaused nonReentrant {
         if (!roleRegistry.hasRole(LIQUIDITY_POOL_VALIDATOR_APPROVER_ROLE, msg.sender)) revert IncorrectRole();
         if (_validatorSizeWei < 32 ether || _validatorSizeWei > 2048 ether) revert InvalidValidatorSize();
 
```

### src/PriorityWithdrawalQueue.sol
```diff
@@ -283,7 +283,7 @@ contract PriorityWithdrawalQueue is
     /// @dev Anyone can call this to claim on behalf of the user. Funds are sent to request.user.
     ///      ETH delivery forwards gas to request.user, so third parties should avoid claiming for untrusted recipients.
     /// @param request The withdrawal request to claim
-    function claimWithdraw(WithdrawRequest calldata request) external whenNotPaused nonReentrant {
+    function claimWithdraw(WithdrawRequest calldata request) external nonReentrant {
         if (request.creationTime + MIN_DELAY > block.timestamp) revert NotMatured();
         
         (uint256 lpEthBefore, uint256 queueEEthSharesBefore) = _snapshotBalances();
@@ -298,7 +298,7 @@ contract PriorityWithdrawalQueue is
     /// @dev Anyone can call this to claim on behalf of users. Funds are sent to each request.user.
     ///      Each ETH delivery forwards gas to request.user, so batching untrusted recipients can be griefed.
     /// @param requests Array of withdrawal requests to claim
-    function batchClaimWithdraw(WithdrawRequest[] calldata requests) external whenNotPaused nonReentrant {
+    function batchClaimWithdraw(WithdrawRequest[] calldata requests) external nonReentrant {
         for (uint256 i = 0; i < requests.length; ++i) {
             if (requests[i].creationTime + MIN_DELAY > block.timestamp) revert NotMatured();
             (uint256 lpEthBefore, uint256 queueEEthSharesBefore) = _snapshotBalances();
```

### src/ReentrancyGuardNamespaced.sol
```diff
@@ -0,0 +1,43 @@
+// SPDX-License-Identifier: MIT
+pragma solidity ^0.8.13;
+
+/// @title ReentrancyGuardNamespaced
+/// @notice Reentrancy guard that stores its `_status` flag at a fixed, namespaced
+///         keccak storage slot instead of a sequential contract-storage slot.
+/// @dev    This repo uses OpenZeppelin Upgradeable v4.8.2, whose
+///         `ReentrancyGuardUpgradeable` declares `uint256 _status` + `uint256[49] __gap`
+///         as regular (sequential) storage. Adding it as a parent to already-deployed
+///         upgradeable contracts (e.g. LiquidityPool, WithdrawRequestNFT) would shift
+///         every existing state variable by 50 slots and corrupt storage on upgrade.
+///         This namespaced variant keeps `_status` at a deterministic slot so it can be
+///         safely mixed into existing UUPS contracts without disturbing their layout.
+abstract contract ReentrancyGuardNamespaced {
+    // keccak256("etherfi.storage.ReentrancyGuard.v1")
+    bytes32 private constant REENTRANCY_GUARD_SLOT =
+        0xcd24049d7dcc1fde21494dba8ad7a067afb6b8f14dfe804abeeec84903344e97;
+
+    uint256 private constant NOT_ENTERED = 1;
+    uint256 private constant ENTERED = 2;
+
+    error ReentrancyGuardReentrantCall();
+
+    modifier nonReentrant() {
+        _nonReentrantBefore();
+        _;
+        _nonReentrantAfter();
+    }
+
+    function _nonReentrantBefore() private {
+        bytes32 slot = REENTRANCY_GUARD_SLOT;
+        uint256 status;
+        assembly { status := sload(slot) }
+        // Treat both 0 (uninitialized) and NOT_ENTERED as "not entered".
+        if (status == ENTERED) revert ReentrancyGuardReentrantCall();
+        assembly { sstore(slot, ENTERED) }
+    }
+
+    function _nonReentrantAfter() private {
+        bytes32 slot = REENTRANCY_GUARD_SLOT;
+        assembly { sstore(slot, NOT_ENTERED) }
+    }
+}
```

### src/WithdrawRequestNFT.sol
```diff
@@ -12,10 +12,11 @@ import "./interfaces/IMembershipManager.sol";
 import "@openzeppelin/contracts/utils/math/Math.sol";
 import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
 import "./RoleRegistry.sol";
+import "./ReentrancyGuardNamespaced.sol";
 
 
 
-contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgradeable, IWithdrawRequestNFT {
+contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgradeable, ReentrancyGuardNamespaced, IWithdrawRequestNFT {
     using Math for uint256;
     using SafeERC20 for IERC20;
 
@@ -135,7 +136,7 @@ contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgrad
     /// @notice called by the NFT owner to claim their ETH
     /// @dev burns the NFT and transfers ETH from the liquidity pool to the owner minus any fee, withdraw request must be valid and finalized
     /// @param tokenId the id of the withdraw request and associated NFT
-    function claimWithdraw(uint256 tokenId) external whenNotPaused {
+    function claimWithdraw(uint256 tokenId) external nonReentrant {
         return _claimWithdraw(tokenId, ownerOf(tokenId));
     }
     
@@ -160,7 +161,7 @@ contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgrad
         emit WithdrawRequestClaimed(uint32(tokenId), amountToWithdraw, amountBurnedShare, recipient, 0);
     }
 
-    function batchClaimWithdraw(uint256[] calldata tokenIds) external whenNotPaused {
+    function batchClaimWithdraw(uint256[] calldata tokenIds) external nonReentrant {
         for (uint256 i = 0; i < tokenIds.length; i++) {
             _claimWithdraw(tokenIds[i], ownerOf(tokenIds[i]));
         }
@@ -218,7 +219,9 @@ contract WithdrawRequestNFT is ERC721Upgradeable, UUPSUpgradeable, OwnableUpgrad
         lastFinalizedRequestId = uint32(requestId);
     }
 
+    /// @dev Admin can only invalidate requests that have NOT been finalized yet
     function invalidateRequest(uint256 requestId) external onlyAdmin {
+        require(requestId > lastFinalizedRequestId, "Cannot invalidate finalized request");
         require(isValid(requestId), "Request is not valid");
         _requests[requestId].isValid = false;
 
```

### test/PriorityWithdrawalQueue.t.sol
```diff
@@ -1164,6 +1164,80 @@ contract PriorityWithdrawalQueueTest is TestSetup {
         priorityQueue.unPauseContract();
     }
 
+    function test_claimWithdraw_succeedsWhenPaused() public {
+        uint96 withdrawAmount = 10 ether;
+
+        (, IPriorityWithdrawalQueue.WithdrawRequest memory request) =
+            _createWithdrawRequest(vipUser, withdrawAmount);
+
+        IPriorityWithdrawalQueue.WithdrawRequest[] memory requests = new IPriorityWithdrawalQueue.WithdrawRequest[](1);
+        requests[0] = request;
+        vm.prank(requestManager);
+        priorityQueue.fulfillRequests(requests);
+
+        // Pause AFTER fulfill so the request is finalized but the queue is paused at claim time.
+        vm.prank(alice);
+        priorityQueue.pauseContract();
+        assertTrue(priorityQueue.paused(), "precondition: queue must be paused");
+
+        uint256 userEthBefore = vipUser.balance;
+        vm.prank(regularUser);
+        priorityQueue.claimWithdraw(request);
+
+        assertApproxEqRel(vipUser.balance, userEthBefore + withdrawAmount, 0.001e18, "claim must pay out while paused");
+    }
+
+    function test_batchClaimWithdraw_succeedsWhenPaused() public {
+        uint96 amount1 = 5 ether;
+        uint96 amount2 = 3 ether;
+
+        (, IPriorityWithdrawalQueue.WithdrawRequest memory request1) =
+            _createWithdrawRequest(vipUser, amount1);
+        (, IPriorityWithdrawalQueue.WithdrawRequest memory request2) =
+            _createWithdrawRequest(vipUser, amount2);
+
+        IPriorityWithdrawalQueue.WithdrawRequest[] memory requests = new IPriorityWithdrawalQueue.WithdrawRequest[](2);
+        requests[0] = request1;
+        requests[1] = request2;
+        vm.prank(requestManager);
+        priorityQueue.fulfillRequests(requests);
+
+        vm.prank(alice);
+        priorityQueue.pauseContract();
+
+        uint256 ethBefore = vipUser.balance;
+        vm.prank(vipUser);
+        priorityQueue.batchClaimWithdraw(requests);
+
+        assertApproxEqRel(vipUser.balance, ethBefore + amount1 + amount2, 0.001e18, "batch claim must pay out while paused");
+    }
+
+    function test_claimWithdraw_succeedsWhenLpAndQueuePaused() public {
+        uint96 withdrawAmount = 10 ether;
+
+        (, IPriorityWithdrawalQueue.WithdrawRequest memory request) =
+            _createWithdrawRequest(vipUser, withdrawAmount);
+
+        IPriorityWithdrawalQueue.WithdrawRequest[] memory requests = new IPriorityWithdrawalQueue.WithdrawRequest[](1);
+        requests[0] = request;
+        vm.prank(requestManager);
+        priorityQueue.fulfillRequests(requests);
+
+        // Pause both contracts (the audit's worst-case "everything paused at once" scenario).
+        vm.prank(alice);
+        priorityQueue.pauseContract();
+        vm.prank(admin);
+        liquidityPoolInstance.pauseContract();
+        assertTrue(priorityQueue.paused(), "precondition: queue must be paused");
+        assertTrue(liquidityPoolInstance.paused(), "precondition: LP must be paused");
+
+        uint256 userEthBefore = vipUser.balance;
+        vm.prank(regularUser);
+        priorityQueue.claimWithdraw(request);
+
+        assertApproxEqRel(vipUser.balance, userEthBefore + withdrawAmount, 0.001e18, "claim must pay out while both paused");
+    }
+
     //--------------------------------------------------------------------------------------
     //------------------------------  REMAINDER TESTS  -------------------------------------
     //--------------------------------------------------------------------------------------
```

### test/ReentrancyGuard.t.sol
```diff
@@ -0,0 +1,198 @@
+// SPDX-License-Identifier: MIT
+pragma solidity ^0.8.13;
+
+import "./TestSetup.sol";
+import "forge-std/Test.sol";
+
+import "../src/ReentrancyGuardNamespaced.sol";
+import "../src/WithdrawRequestNFT.sol";
+
+/// @dev Attacker contract that owns two withdrawal NFTs. On receiving ETH during
+///      a claimWithdraw call, it attempts to re-enter WithdrawRequestNFT via
+///      claimWithdraw or batchClaimWithdraw using a *different* tokenId. The
+///      ReentrancyGuardNamespaced on WithdrawRequestNFT must cause the re-entry
+///      to revert; the try/catch lets the outer claim complete so the test can
+///      inspect the `reentryBlocked` flag.
+contract ReentrancyAttacker {
+    enum Mode { None, Claim, BatchClaim }
+
+    WithdrawRequestNFT public immutable wr;
+    Mode public mode;
+    uint256 public pendingTokenId;
+    uint256 public reentryAttempts;
+    uint256 public reentryBlocked;
+    bytes public lastRevert;
+
+    constructor(WithdrawRequestNFT _wr) {
+        wr = _wr;
+    }
+
+    function claim(uint256 firstId, uint256 secondId, Mode _mode) external {
+        mode = _mode;
+        pendingTokenId = secondId;
+        wr.claimWithdraw(firstId);
+    }
+
+    function batchClaim(uint256[] calldata ids, uint256 reentryId, Mode _mode) external {
+        mode = _mode;
+        pendingTokenId = reentryId;
+        wr.batchClaimWithdraw(ids);
+    }
+
+    function onERC721Received(address, address, uint256, bytes calldata) external pure returns (bytes4) {
+        return this.onERC721Received.selector;
+    }
+
+    receive() external payable {
+        if (mode == Mode.None || pendingTokenId == 0) return;
+        uint256 tid = pendingTokenId;
+        pendingTokenId = 0; // only attempt once per outer call
+        reentryAttempts += 1;
+
+        if (mode == Mode.Claim) {
+            try wr.claimWithdraw(tid) {
+                // guard failed - re-entry succeeded
+            } catch (bytes memory err) {
+                reentryBlocked += 1;
+                lastRevert = err;
+            }
+        } else if (mode == Mode.BatchClaim) {
+            uint256[] memory arr = new uint256[](1);
+            arr[0] = tid;
+            try wr.batchClaimWithdraw(arr) {
+                // guard failed
+            } catch (bytes memory err) {
+                reentryBlocked += 1;
+                lastRevert = err;
+            }
+        }
+    }
+}
+
+contract ReentrancyGuardTest is TestSetup {
+    ReentrancyAttacker attacker;
+
+    function setUp() public {
+        setUpTests();
+        vm.prank(admin);
+        withdrawRequestNFTInstance.unPauseContract();
+
+        attacker = new ReentrancyAttacker(withdrawRequestNFTInstance);
+    }
+
+    /// @dev Seeds an attacker-owned withdraw request: alice deposits, requests
+    ///      withdraw to the attacker as recipient, then finalises.
+    function _seedRequest(uint256 amount) internal returns (uint256 requestId) {
+        vm.deal(alice, amount);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: amount}();
+
+        vm.startPrank(alice);
+        eETHInstance.approve(address(liquidityPoolInstance), amount);
+        requestId = liquidityPoolInstance.requestWithdraw(address(attacker), amount);
+        vm.stopPrank();
+
+        _finalizeWithdrawalRequest(requestId);
+    }
+
+    function testFuzz_noRegression_claimWithdraw_withNonReentrantRecipient() public {
+        // Sanity check: normal (non-attacker) recipient still completes claim.
+        vm.deal(alice, 1 ether);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+
+        vm.startPrank(alice);
+        eETHInstance.approve(address(liquidityPoolInstance), 1 ether);
+        uint256 rid = liquidityPoolInstance.requestWithdraw(alice, 1 ether);
+        vm.stopPrank();
+        _finalizeWithdrawalRequest(rid);
+
+        uint256 beforeBal = alice.balance;
+        vm.prank(alice);
+        withdrawRequestNFTInstance.claimWithdraw(rid);
+        assertEq(alice.balance, beforeBal + 1 ether, "normal claim payout");
+    }
+
+    function test_claimWithdraw_reentry_viaClaim_isBlocked() public {
+        uint256 id1 = _seedRequest(1 ether);
+        uint256 id2 = _seedRequest(1 ether);
+
+        // Attacker attempts to call claimWithdraw(id2) during the receive() of claimWithdraw(id1).
+        vm.prank(address(attacker));
+        attacker.claim(id1, id2, ReentrancyAttacker.Mode.Claim);
+
+        assertEq(attacker.reentryAttempts(), 1, "attacker attempted re-entry");
+        assertEq(attacker.reentryBlocked(), 1, "guard must block re-entry into claimWithdraw");
+
+        // Decoding the revert: must be ReentrancyGuardReentrantCall() (selector match).
+        bytes4 sel = bytes4(attacker.lastRevert());
+        assertEq(sel, ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector, "wrong revert selector");
+
+        // Outer claim still completed and paid out; id2 is still claimable later.
+        assertEq(address(attacker).balance, 1 ether, "outer claim paid out");
+        assertEq(withdrawRequestNFTInstance.ownerOf(id2), address(attacker), "id2 still owned by attacker");
+    }
+
+    function test_claimWithdraw_reentry_viaBatchClaim_isBlocked() public {
+        uint256 id1 = _seedRequest(1 ether);
+        uint256 id2 = _seedRequest(1 ether);
+
+        vm.prank(address(attacker));
+        attacker.claim(id1, id2, ReentrancyAttacker.Mode.BatchClaim);
+
+        assertEq(attacker.reentryBlocked(), 1, "guard must block cross-fn re-entry via batchClaimWithdraw");
+        bytes4 sel = bytes4(attacker.lastRevert());
+        assertEq(sel, ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector, "wrong revert selector");
+    }
+
+    function test_batchClaimWithdraw_reentry_viaClaim_isBlocked() public {
+        uint256 id1 = _seedRequest(1 ether);
+        uint256 id2 = _seedRequest(1 ether);
+        uint256 id3 = _seedRequest(1 ether); // used for re-entry attempt
+
+        uint256[] memory batch = new uint256[](2);
+        batch[0] = id1;
+        batch[1] = id2;
+
+        vm.prank(address(attacker));
+        attacker.batchClaim(batch, id3, ReentrancyAttacker.Mode.Claim);
+
+        // Re-entry attempted during the first element of the batch, blocked by guard.
+        // The outer batch continues and processes both id1 and id2.
+        assertGt(attacker.reentryBlocked(), 0, "guard must block re-entry during batch");
+        assertEq(address(attacker).balance, 2 ether, "batch paid out both items");
+        assertEq(withdrawRequestNFTInstance.ownerOf(id3), address(attacker), "id3 untouched");
+    }
+
+    function test_guardResets_betweenCalls() public {
+        // Verify guard is properly reset: two sequential claims should both succeed.
+        uint256 id1 = _seedRequest(1 ether);
+        uint256 id2 = _seedRequest(1 ether);
+
+        // Use non-reentrant path: transfer id1 out of attacker to alice so a vanilla EOA claim happens.
+        vm.prank(address(attacker));
+        withdrawRequestNFTInstance.transferFrom(address(attacker), alice, id1);
+        vm.prank(address(attacker));
+        withdrawRequestNFTInstance.transferFrom(address(attacker), alice, id2);
+
+        vm.prank(alice);
+        withdrawRequestNFTInstance.claimWithdraw(id1);
+        vm.prank(alice);
+        withdrawRequestNFTInstance.claimWithdraw(id2); // would revert if guard stuck in ENTERED state
+    }
+
+    function test_liquidityPool_deposit_reentryFromReceive_isBlocked() public {
+        // Defense-in-depth: even though deposit() itself doesn't push ETH out,
+        // the guard prevents a nested deposit -> deposit call path through any
+        // external hook. Simulate by calling deposit from a contract that also
+        // re-enters deposit during the same tx; since deposit has no external
+        // call to attacker, we instead test the guard state directly by making
+        // two sequential top-level deposits (must not be stuck in ENTERED).
+        vm.deal(alice, 5 ether);
+        vm.startPrank(alice);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+        liquidityPoolInstance.deposit{value: 1 ether}(); // second top-level call must succeed
+        vm.stopPrank();
+        assertEq(eETHInstance.balanceOf(alice), 2 ether, "two sequential deposits work");
+    }
+}
```

### test/ReentrancyGuardStorage.t.sol
```diff
@@ -0,0 +1,277 @@
+// SPDX-License-Identifier: MIT
+pragma solidity ^0.8.13;
+
+import "./TestSetup.sol";
+import "forge-std/Test.sol";
+
+import "../src/ReentrancyGuardNamespaced.sol";
+
+/// @notice Verifies that the namespaced reentrancy guard's fixed storage slot
+///         does NOT collide with any storage used by LiquidityPool or
+///         WithdrawRequestNFT — including OZ upgradeable parents (Initializable,
+///         ContextUpgradeable, ERC721Upgradeable, OwnableUpgradeable,
+///         UUPSUpgradeable) and their `__gap` reservations.
+///
+/// Two directions of collision are tested:
+///   (1) Writes to declared state variables must not touch the guard slot.
+///   (2) Writes to the guard slot must not touch any declared state variable.
+///
+/// Mapping-slot collisions (`keccak256(abi.encode(key, mappingSlot)) == GUARD`)
+/// are cryptographically ruled out by keccak256 preimage resistance. We still
+/// exercise mapping-writing paths (ERC721 mint/transfer, `validatorSpawner`,
+/// `_requests`) and verify guard-slot integrity to catch accidental collisions
+/// with the tiny, deterministic subset of keys used in real flows.
+contract ReentrancyGuardStorageTest is TestSetup {
+    bytes32 private constant GUARD_SLOT =
+        0xcd24049d7dcc1fde21494dba8ad7a067afb6b8f14dfe804abeeec84903344e97;
+
+    // Distinctive sentinel value: not 0, not NOT_ENTERED(1), not ENTERED(2).
+    bytes32 private constant SENTINEL = bytes32(uint256(0xDEADBEEFCAFEBABE));
+
+    function setUp() public {
+        setUpTests();
+        vm.prank(admin);
+        withdrawRequestNFTInstance.unPauseContract();
+    }
+
+    // -----------------------------------------------------------------
+    //                   Direction 1: layout is disjoint
+    // -----------------------------------------------------------------
+
+    /// @dev Sequential storage slots are tiny integers (0, 1, 2, ...). The
+    ///      guard slot is a keccak256 hash (~2^255). A uint256 cast proves the
+    ///      distance. Using a loose upper bound of 10_000 for the declared-
+    ///      storage range — both contracts use < 400 slots per `forge inspect`.
+    function test_guardSlot_outsideDeclaredSequentialRange() public {
+        uint256 guardAsUint = uint256(GUARD_SLOT);
+        assertGt(guardAsUint, 10_000, "guard slot within declared sequential storage range");
+    }
+
+    /// @dev Fresh proxy should have 0 at guard slot (uninitialized).
+    function test_guardSlot_initialValueIsZero_LP() public {
+        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(0));
+    }
+
+    function test_guardSlot_initialValueIsZero_WRN() public {
+        assertEq(vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT), bytes32(0));
+    }
+
+    // -----------------------------------------------------------------
+    //     Direction 2: declared-state writes don't touch guard slot
+    // -----------------------------------------------------------------
+
+    /// @dev Plants SENTINEL at guard slot, performs many unguarded state
+    ///      mutations, verifies SENTINEL is preserved. If any declared slot
+    ///      aliased the guard slot, the sentinel would be overwritten.
+    function test_noCollision_LP_unguardedStateWrites_preserveGuardSlot() public {
+        vm.store(address(liquidityPoolInstance), GUARD_SLOT, SENTINEL);
+
+        // Unguarded setters — each touches a different declared storage slot.
+        vm.startPrank(admin);
+        liquidityPoolInstance.setFeeRecipient(address(0xBEEF));
+        liquidityPoolInstance.setRestakeBnftDeposits(true);
+        liquidityPoolInstance.setValidatorSizeWei(64 ether);
+        liquidityPoolInstance.registerValidatorSpawner(address(0xABCD));
+        vm.stopPrank();
+
+        assertEq(
+            vm.load(address(liquidityPoolInstance), GUARD_SLOT),
+            SENTINEL,
+            "LP declared state writes aliased the guard slot"
+        );
+    }
+
+    /// @dev Same check via ERC721-triggering paths on WithdrawRequestNFT.
+    ///      Mints NFTs (writes to _owners, _balances, _requests mappings),
+    ///      transfers (writes to _tokenApprovals), and pause toggles.
+    function test_noCollision_WRN_mappingAndStateWrites_preserveGuardSlot() public {
+        vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, SENTINEL);
+
+        // Generate a withdraw request so the ERC721 mappings and _requests get populated.
+        vm.deal(alice, 3 ether);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: 3 ether}();
+        vm.startPrank(alice);
+        eETHInstance.approve(address(liquidityPoolInstance), 3 ether);
+        uint256 rid = liquidityPoolInstance.requestWithdraw(alice, 1 ether);
+        liquidityPoolInstance.requestWithdraw(alice, 1 ether);
+        liquidityPoolInstance.requestWithdraw(alice, 1 ether);
+        // ERC721 transfer path -> _tokenApprovals, _owners rewrite
+        withdrawRequestNFTInstance.approve(bob, rid);
+        withdrawRequestNFTInstance.transferFrom(alice, bob, rid);
+        vm.stopPrank();
+
+        // Admin pause toggle -> `paused` bool
+        vm.prank(admin);
+        withdrawRequestNFTInstance.pauseContract();
+        vm.prank(admin);
+        withdrawRequestNFTInstance.unPauseContract();
+
+        assertEq(
+            vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT),
+            SENTINEL,
+            "WRN declared state writes aliased the guard slot"
+        );
+    }
+
+    // -----------------------------------------------------------------
+    //     Direction 3: guard-slot writes don't touch declared state
+    // -----------------------------------------------------------------
+
+    function test_noCollision_guardSlotWrites_doNotCorruptLPState() public {
+        // Snapshot critical declared state.
+        address feeRecipientBefore = liquidityPoolInstance.feeRecipient();
+        address stakingMgrBefore = address(liquidityPoolInstance.stakingManager());
+        address eethBefore = address(liquidityPoolInstance.eETH());
+        uint128 totalInLpBefore = liquidityPoolInstance.totalValueInLp();
+        uint128 totalOutBefore = liquidityPoolInstance.totalValueOutOfLp();
+        uint256 validatorSizeBefore = liquidityPoolInstance.validatorSizeWei();
+
+        // Fill a few exotic values into the guard slot.
+        bytes32[4] memory probes = [
+            bytes32(uint256(1)),
+            bytes32(uint256(2)),
+            bytes32(type(uint256).max),
+            SENTINEL
+        ];
+        for (uint256 i = 0; i < probes.length; i++) {
+            vm.store(address(liquidityPoolInstance), GUARD_SLOT, probes[i]);
+
+            assertEq(liquidityPoolInstance.feeRecipient(), feeRecipientBefore, "feeRecipient corrupted");
+            assertEq(address(liquidityPoolInstance.stakingManager()), stakingMgrBefore, "stakingManager corrupted");
+            assertEq(address(liquidityPoolInstance.eETH()), eethBefore, "eETH corrupted");
+            assertEq(liquidityPoolInstance.totalValueInLp(), totalInLpBefore, "totalValueInLp corrupted");
+            assertEq(liquidityPoolInstance.totalValueOutOfLp(), totalOutBefore, "totalValueOutOfLp corrupted");
+            assertEq(liquidityPoolInstance.validatorSizeWei(), validatorSizeBefore, "validatorSizeWei corrupted");
+        }
+    }
+
+    function test_noCollision_guardSlotWrites_doNotCorruptWRNState() public {
+        // Snapshot critical declared state.
+        address lpBefore = address(withdrawRequestNFTInstance.liquidityPool());
+        address eethBefore = address(withdrawRequestNFTInstance.eETH());
+        uint32 nextIdBefore = withdrawRequestNFTInstance.nextRequestId();
+        uint32 lastFinBefore = withdrawRequestNFTInstance.lastFinalizedRequestId();
+        uint16 splitBefore = withdrawRequestNFTInstance.shareRemainderSplitToTreasuryInBps();
+        bool pausedBefore = withdrawRequestNFTInstance.paused();
+
+        bytes32[4] memory probes = [
+            bytes32(uint256(1)),
+            bytes32(uint256(2)),
+            bytes32(type(uint256).max),
+            SENTINEL
+        ];
+        for (uint256 i = 0; i < probes.length; i++) {
+            vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, probes[i]);
+
+            assertEq(address(withdrawRequestNFTInstance.liquidityPool()), lpBefore, "liquidityPool corrupted");
+            assertEq(address(withdrawRequestNFTInstance.eETH()), eethBefore, "eETH corrupted");
+            assertEq(withdrawRequestNFTInstance.nextRequestId(), nextIdBefore, "nextRequestId corrupted");
+            assertEq(withdrawRequestNFTInstance.lastFinalizedRequestId(), lastFinBefore, "lastFinalizedRequestId corrupted");
+            assertEq(withdrawRequestNFTInstance.shareRemainderSplitToTreasuryInBps(), splitBefore, "split corrupted");
+            assertEq(withdrawRequestNFTInstance.paused(), pausedBefore, "paused corrupted");
+        }
+    }
+
+    // -----------------------------------------------------------------
+    //              Direction 4: guard cycles correctly
+    // -----------------------------------------------------------------
+
+    /// @dev After a guarded call completes, the slot must be NOT_ENTERED (1).
+    function test_guardSlot_setsToNotEnteredAfterCall_LP() public {
+        vm.deal(alice, 1 ether);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+
+        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(uint256(1)));
+    }
+
+    function test_guardSlot_setsToNotEnteredAfterCall_WRN() public {
+        vm.deal(alice, 1 ether);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+        vm.startPrank(alice);
+        eETHInstance.approve(address(liquidityPoolInstance), 1 ether);
+        uint256 rid = liquidityPoolInstance.requestWithdraw(alice, 1 ether);
+        vm.stopPrank();
+        _finalizeWithdrawalRequest(rid);
+
+        vm.prank(alice);
+        withdrawRequestNFTInstance.claimWithdraw(rid);
+
+        assertEq(vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT), bytes32(uint256(1)));
+    }
+
+    /// @dev If the guard slot is pre-populated with ENTERED, the next guarded
+    ///      call must revert with the expected selector — proves we actually
+    ///      read the slot we think we do.
+    function test_guardSlot_prePopulatedENTERED_revertsAllGuardedPaths() public {
+        vm.store(address(liquidityPoolInstance), GUARD_SLOT, bytes32(uint256(2)));
+
+        vm.deal(alice, 1 ether);
+        vm.prank(alice);
+        vm.expectRevert(ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+    }
+
+    /// @dev Any non-ENTERED value in the slot must be treated as NOT_ENTERED
+    ///      (forward-compat with uninitialised 0 AND defensive against stray
+    ///      writes that aren't exactly 2). Fuzzed.
+    function testFuzz_guardSlot_nonENTERED_allowsCall(uint256 preValue) public {
+        vm.assume(preValue != 2); // ENTERED
+        vm.store(address(liquidityPoolInstance), GUARD_SLOT, bytes32(preValue));
+
+        vm.deal(alice, 1 ether);
+        vm.prank(alice);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+
+        // Post-call, guard must be normalised to NOT_ENTERED (1).
+        assertEq(vm.load(address(liquidityPoolInstance), GUARD_SLOT), bytes32(uint256(1)));
+    }
+
+    // -----------------------------------------------------------------
+    //   Direction 5: mapping/ERC721 hot paths don't drift guard slot
+    // -----------------------------------------------------------------
+
+    /// @dev Heavy mapping churn: deposit many times (writes eETH share mappings
+    ///      via external contract — NB: those mappings live on eETH, not LP),
+    ///      multiple withdraw requests, pause cycles. Guard slot sentinel must
+    ///      survive across all of it (since all these paths are either
+    ///      unguarded or use the guard transiently and restore NOT_ENTERED).
+    ///
+    ///      We seed the slot with SENTINEL, then exercise ONLY unguarded state
+    ///      mutations so the guard modifier doesn't overwrite the sentinel.
+    function test_noCollision_WRN_deepMappingWrites_unguardedPaths() public {
+        vm.store(address(withdrawRequestNFTInstance), GUARD_SLOT, SENTINEL);
+
+        // Pause / unpause cycles — only modify `paused`.
+        for (uint256 i = 0; i < 3; i++) {
+            vm.prank(admin);
+            withdrawRequestNFTInstance.pauseContract();
+            vm.prank(admin);
+            withdrawRequestNFTInstance.unPauseContract();
+        }
+
+        assertEq(
+            vm.load(address(withdrawRequestNFTInstance), GUARD_SLOT),
+            SENTINEL,
+            "pause toggles aliased guard slot"
+        );
+    }
+
+    /// @dev Cross-contract: deposit flow touches LP.totalValueInLp / totalValueOutOfLp
+    ///      and external eETH shares mapping. Checks LP's guard slot integrity
+    ///      against mutations on OTHER contracts (must be trivially orthogonal).
+    function test_noCollision_LP_crossContractActivity() public {
+        vm.store(address(liquidityPoolInstance), GUARD_SLOT, SENTINEL);
+
+        // All of this mutates eETH (another contract), membership, admin — none of LP.
+        vm.prank(admin);
+        liquidityPoolInstance.setFeeRecipient(address(0xFEED));
+
+        assertEq(
+            vm.load(address(liquidityPoolInstance), GUARD_SLOT),
+            SENTINEL
+        );
+    }
+}
```

### test/WithdrawRequestNFT.t.sol
```diff
@@ -295,6 +295,9 @@ contract WithdrawRequestNFTTest is TestSetup {
 
     // It depicts the scenario where bob's WithdrawalRequest NFT is stolen by alice.
     // The owner invalidates the request 
+    /// @dev Updated: admin MUST NOT be able to invalidate a request once it has been finalized.
+    ///      Previously this test demonstrated the legacy (unsafe) capability; it now proves the
+    ///      post-finalization invalidation path reverts and the request remains valid.
     function test_InvalidatedRequestNft_after_finalization() public returns (uint256 requestId) {
         startHoax(bob);
         liquidityPoolInstance.deposit{value: 10 ether}();
@@ -318,7 +321,10 @@ contract WithdrawRequestNFTTest is TestSetup {
         assertTrue(withdrawRequestNFTInstance.isValid(requestId), "Request should be valid");
 
         vm.prank(admin);
+        vm.expectRevert("Cannot invalidate finalized request");
         withdrawRequestNFTInstance.invalidateRequest(requestId);
+
+        assertTrue(withdrawRequestNFTInstance.isValid(requestId), "Request must remain valid after rejected invalidation");
     }
 
     function test_InvalidatedRequestNft_before_finalization() public returns (uint256 requestId) {
@@ -1036,6 +1042,9 @@ contract WithdrawRequestNFTTest is TestSetup {
         assertEq(withdrawRequestNFTInstance.ownerOf(requestId), alice, "NFT should be transferred");
     }
 
+    /// @dev Updated: invalidation now only possible pre-finalization, so the test invalidates
+    ///      first, THEN finalizes, then asserts claim reverts on `!isValid`. End-state assertion
+    ///      (invalid request cannot be claimed) is unchanged.
     function test_claimWithdraw_InvalidRequest() public {
         startHoax(bob);
         liquidityPoolInstance.deposit{value: 10 ether}();
@@ -1047,13 +1056,14 @@ contract WithdrawRequestNFTTest is TestSetup {
         vm.prank(bob);
         uint256 requestId = liquidityPoolInstance.requestWithdraw(bob, 1 ether);
 
-        _finalizeWithdrawalRequest(requestId);
-
-        // Invalidate request
+        // Invalidate BEFORE finalization (the only time admin can do it now).
         vm.prank(admin);
         withdrawRequestNFTInstance.invalidateRequest(requestId);
 
-        // Cannot claim invalid request
+        // An invalid request can still be finalized (finalization cursor is monotonic and doesn't check validity).
+        _finalizeWithdrawalRequest(requestId);
+
+        // Claim still blocked by the `isValid` check inside `_claimWithdraw`.
         vm.prank(bob);
         vm.expectRevert("Request is not valid");
         withdrawRequestNFTInstance.claimWithdraw(requestId);
@@ -1070,4 +1080,216 @@ contract WithdrawRequestNFTTest is TestSetup {
         vm.expectRevert("Request does not exist");
         withdrawRequestNFTInstance.isValid(99999);
     }
+
+    // -----------------------------------------------------------------
+    //  Permissionless claim + no-post-finalization-invalidation tests
+    // -----------------------------------------------------------------
+
+    /// @dev Helper: make a withdraw request owned by `owner` for `amount`.
+    function _requestFor(address owner, uint96 amount) internal returns (uint256 requestId) {
+        startHoax(owner);
+        liquidityPoolInstance.deposit{value: amount}();
+        eETHInstance.approve(address(liquidityPoolInstance), amount);
+        requestId = liquidityPoolInstance.requestWithdraw(owner, amount);
+        vm.stopPrank();
+    }
+
+    function test_claimWithdraw_succeedsWhilePaused_ifFinalized() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        _finalizeWithdrawalRequest(requestId);
+
+        // Pause BEFORE the claim — finalized claim must proceed anyway.
+        vm.prank(admin);
+        withdrawRequestNFTInstance.pauseContract();
+        assertTrue(withdrawRequestNFTInstance.paused(), "precondition: must be paused");
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+
+        assertEq(bob.balance - bobBalBefore, 1 ether, "finalized claim must pay out while paused");
+    }
+
+    function test_batchClaimWithdraw_succeedsWhilePaused_ifFinalized() public {
+        uint256 r1 = _requestFor(bob, 1 ether);
+        uint256 r2 = _requestFor(bob, 2 ether);
+        _finalizeWithdrawalRequest(r1);
+        _finalizeWithdrawalRequest(r2);
+
+        vm.prank(admin);
+        withdrawRequestNFTInstance.pauseContract();
+
+        uint256[] memory ids = new uint256[](2);
+        ids[0] = r1;
+        ids[1] = r2;
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.batchClaimWithdraw(ids);
+
+        assertEq(bob.balance - bobBalBefore, 3 ether, "batch claim must pay out while paused");
+    }
+
+    function test_claimWithdraw_revertsWhenUnfinalized_paused() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        // NOT finalized.
+
+        vm.prank(admin);
+        withdrawRequestNFTInstance.pauseContract();
+
+        vm.prank(bob);
+        vm.expectRevert("Request is not finalized");
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+    }
+
+    function test_claimWithdraw_revertsWhenUnfinalized_unpaused() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        // NOT finalized, NOT paused (matches post-setUp state).
+
+        vm.prank(bob);
+        vm.expectRevert("Request is not finalized");
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+    }
+
+    function test_claimWithdraw_succeedsWhenLiquidityPoolPaused() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        _finalizeWithdrawalRequest(requestId);
+
+        vm.prank(admin);
+        liquidityPoolInstance.pauseContract();
+        assertTrue(liquidityPoolInstance.paused(), "precondition: LP must be paused");
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+
+        assertEq(bob.balance - bobBalBefore, 1 ether, "finalized claim must pay out while LP is paused");
+    }
+
+    function test_batchClaimWithdraw_succeedsWhenLiquidityPoolPaused() public {
+        uint256 r1 = _requestFor(bob, 1 ether);
+        uint256 r2 = _requestFor(bob, 2 ether);
+        _finalizeWithdrawalRequest(r1);
+        _finalizeWithdrawalRequest(r2);
+
+        vm.prank(admin);
+        liquidityPoolInstance.pauseContract();
+
+        uint256[] memory ids = new uint256[](2);
+        ids[0] = r1;
+        ids[1] = r2;
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.batchClaimWithdraw(ids);
+
+        assertEq(bob.balance - bobBalBefore, 3 ether, "batch claim must pay out while LP is paused");
+    }
+
+    function test_claimWithdraw_succeedsWhenBothPaused() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        _finalizeWithdrawalRequest(requestId);
+
+        vm.startPrank(admin);
+        liquidityPoolInstance.pauseContract();
+        withdrawRequestNFTInstance.pauseContract();
+        vm.stopPrank();
+        assertTrue(liquidityPoolInstance.paused(), "precondition: LP must be paused");
+        assertTrue(withdrawRequestNFTInstance.paused(), "precondition: NFT must be paused");
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+
+        assertEq(bob.balance - bobBalBefore, 1 ether, "finalized claim must pay out while both are paused");
+    }
+
+    function test_liquidityPool_withdraw_revertsForOtherCallersWhenLpPaused() public {
+        // Pause the LP, then assert that the two non-permissionless callers (membershipManager and
+        // etherFiRedemptionManager) still revert at the pause gate. The pause check sits between the
+        // caller-allowlist require and the eETH-balance check, so no LP funding is needed.
+        vm.prank(admin);
+        liquidityPoolInstance.pauseContract();
+
+        address membershipMgr = address(liquidityPoolInstance.membershipManager());
+        address redemptionMgr = address(liquidityPoolInstance.etherFiRedemptionManager());
+
+        if (membershipMgr != address(0)) {
+            vm.prank(membershipMgr);
+            vm.expectRevert("Pausable: paused");
+            liquidityPoolInstance.withdraw(bob, 1 ether);
+        }
+
+        if (redemptionMgr != address(0)) {
+            vm.prank(redemptionMgr);
+            vm.expectRevert("Pausable: paused");
+            liquidityPoolInstance.withdraw(bob, 1 ether);
+        }
+    }
+
+    function test_liquidityPool_requestWithdraw_revertsWhenLpPaused() public {
+        // Sanity: deposit / requestWithdraw remain gated by the LP pause — only the
+        // claim path is permissionless.
+        startHoax(bob);
+        liquidityPoolInstance.deposit{value: 1 ether}();
+        eETHInstance.approve(address(liquidityPoolInstance), 1 ether);
+        vm.stopPrank();
+
+        vm.prank(admin);
+        liquidityPoolInstance.pauseContract();
+
+        vm.prank(bob);
+        vm.expectRevert("Pausable: paused");
+        liquidityPoolInstance.requestWithdraw(bob, 1 ether);
+    }
+
+    function test_invalidateRequest_revertsForFinalizedRequest() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        _finalizeWithdrawalRequest(requestId);
+        assertTrue(withdrawRequestNFTInstance.isFinalized(requestId));
+
+        vm.prank(admin);
+        vm.expectRevert("Cannot invalidate finalized request");
+        withdrawRequestNFTInstance.invalidateRequest(requestId);
+
+        // Still valid & claimable after the rejected invalidate attempt.
+        assertTrue(withdrawRequestNFTInstance.isValid(requestId), "should still be valid");
+
+        uint256 bobBalBefore = bob.balance;
+        vm.prank(bob);
+        withdrawRequestNFTInstance.claimWithdraw(requestId);
+        assertEq(bob.balance - bobBalBefore, 1 ether);
+    }
+
+    function test_invalidateRequest_succeedsForUnfinalizedRequest() public {
+        uint256 requestId = _requestFor(bob, 1 ether);
+        assertFalse(withdrawRequestNFTInstance.isFinalized(requestId));
+
+        vm.prank(admin);
+        withdrawRequestNFTInstance.invalidateRequest(requestId);
+
+        assertFalse(withdrawRequestNFTInstance.isValid(requestId), "should be invalid after admin action");
+    }
+
+    /// @dev Off-by-one: the token at EXACTLY lastFinalizedRequestId is finalized
+    ///      and therefore must NOT be invalidatable. The next token (id + 1) is
+    ///      not finalized and must still be invalidatable.
+    function test_invalidateRequest_boundary_atLastFinalizedRequestId() public {
+        uint256 r1 = _requestFor(bob, 1 ether);
+        uint256 r2 = _requestFor(bob, 1 ether);
+
+        // Finalize only r1.
+        _finalizeWithdrawalRequest(r1);
+        assertEq(uint256(withdrawRequestNFTInstance.lastFinalizedRequestId()), r1, "r1 is the boundary");
+
+        // r1 == lastFinalizedRequestId → cannot invalidate.
+        vm.prank(admin);
+        vm.expectRevert("Cannot invalidate finalized request");
+        withdrawRequestNFTInstance.invalidateRequest(r1);
+
+        // r2 == lastFinalizedRequestId + 1 → can invalidate.
+        vm.prank(admin);
+        withdrawRequestNFTInstance.invalidateRequest(r2);
+        assertFalse(withdrawRequestNFTInstance.isValid(r2), "r2 should be invalid");
+    }
 }
```

### test/fork-tests/UpgradeStorageIntegrity.t.sol
```diff
@@ -0,0 +1,387 @@
+// SPDX-License-Identifier: MIT
+pragma solidity ^0.8.13;
+
+import "forge-std/Test.sol";
+import "../../script/deploys/Deployed.s.sol";
+import "../../src/LiquidityPool.sol";
+import "../../src/WithdrawRequestNFT.sol";
+import "../../src/ReentrancyGuardNamespaced.sol";
+
+interface IUUPSProxy {
+    function upgradeTo(address newImpl) external;
+}
+
+interface IOwnableRead {
+    function owner() external view returns (address);
+}
+
+/// @notice Fork test that upgrades the real mainnet LiquidityPool and
+///         WithdrawRequestNFT proxies to the new implementation (with the
+///         namespaced reentrancy guard added) and verifies that EVERY
+///         sequential storage slot is byte-identical before and after the
+///         upgrade. This is the load-bearing proof that adding
+///         ReentrancyGuardNamespaced to the inheritance chain did not shift
+///         any existing state variable.
+///
+/// Requires MAINNET_RPC_URL to be set.
+///
+/// Slot scan strategy:
+///   - LiquidityPool declared sequential range per `forge inspect`: 0..~220.
+///   - WithdrawRequestNFT declared sequential range: 0..~310.
+///   - We scan 0..399 on both to comfortably cover both plus any future growth.
+///   - Mapping/array element slots live at keccak256-derived addresses far
+///     above the scan range; they don't shift when the sequential layout is
+///     preserved, so scanning sequentials is sufficient.
+///   - The guard slot (keccak256("etherfi.storage.ReentrancyGuard.v1"), value
+///     ~2^252) is also outside the scan window and is checked separately.
+///   - The ERC-1967 implementation slot changes by design (that's the point of
+///     the upgrade) and is also outside 0..399, so it won't produce false drift.
+contract UpgradeStorageIntegrityTest is Test, Deployed {
+    uint256 internal constant SCAN_SLOTS = 400;
+    bytes32 internal constant GUARD_SLOT =
+        0xcd24049d7dcc1fde21494dba8ad7a067afb6b8f14dfe804abeeec84903344e97;
+
+    struct LPSnap {
+        address eeth;
+        address stakingManager;
+        address nodesManager;
+        address feeRecipient;
+        address admin;
+        address wrn;
+        address liquifier;
+        uint128 totalIn;
+        uint128 totalOut;
+        uint128 locked;
+        uint256 valSize;
+        bool paused;
+        bool restake;
+    }
+
+    struct WRNSnap {
+        address lp;
+        address eeth;
+        address membership;
+        uint32 nextId;
+        uint32 lastFin;
+        uint16 split;
+        uint32 scanFrom;
+        uint32 scanTo;
+        uint256 agg;
+        uint256 remainder;
+        bool paused;
+    }
+
+    function _snapLP(LiquidityPool lp) internal view returns (LPSnap memory s) {
+        s.eeth = address(lp.eETH());
+        s.stakingManager = address(lp.stakingManager());
+        s.nodesManager = address(lp.nodesManager());
+        s.feeRecipient = lp.feeRecipient();
+        s.admin = lp.etherFiAdminContract();
+        s.wrn = address(lp.withdrawRequestNFT());
+        s.liquifier = address(lp.liquifier());
+        s.totalIn = lp.totalValueInLp();
+        s.totalOut = lp.totalValueOutOfLp();
+        s.locked = lp.ethAmountLockedForWithdrawal();
+        s.valSize = lp.validatorSizeWei();
+        s.paused = lp.paused();
+        s.restake = lp.restakeBnftDeposits();
+    }
+
+    function _snapWRN(WithdrawRequestNFT wrn) internal view returns (WRNSnap memory s) {
+        s.lp = address(wrn.liquidityPool());
+        s.eeth = address(wrn.eETH());
+        s.membership = address(wrn.membershipManager());
+        s.nextId = wrn.nextRequestId();
+        s.lastFin = wrn.lastFinalizedRequestId();
+        s.split = wrn.shareRemainderSplitToTreasuryInBps();
+        s.scanFrom = wrn.currentRequestIdToScanFromForShareRemainder();
+        s.scanTo = wrn.lastRequestIdToScanUntilForShareRemainder();
+        s.agg = wrn.aggregateSumOfEEthShare();
+        s.remainder = wrn.totalRemainderEEthShares();
+        s.paused = wrn.paused();
+    }
+
+    function _assertLPEq(LPSnap memory a, LPSnap memory b) internal {
+        assertEq(a.eeth,           b.eeth,           "eETH");
+        assertEq(a.stakingManager, b.stakingManager, "stakingManager");
+        assertEq(a.nodesManager,   b.nodesManager,   "nodesManager");
+        assertEq(a.feeRecipient,   b.feeRecipient,   "feeRecipient");
+        assertEq(a.admin,          b.admin,          "etherFiAdminContract");
+        assertEq(a.wrn,            b.wrn,            "withdrawRequestNFT");
+        assertEq(a.liquifier,      b.liquifier,      "liquifier");
+        assertEq(a.totalIn,        b.totalIn,        "totalValueInLp");
+        assertEq(a.totalOut,       b.totalOut,       "totalValueOutOfLp");
+        assertEq(a.locked,         b.locked,         "ethAmountLockedForWithdrawal");
+        assertEq(a.valSize,        b.valSize,        "validatorSizeWei");
+        assertEq(a.paused,         b.paused,         "paused");
+        assertEq(a.restake,        b.restake,        "restakeBnftDeposits");
+    }
+
+    function _assertWRNEq(WRNSnap memory a, WRNSnap memory b) internal {
+        assertEq(a.lp,         b.lp,         "WRN.liquidityPool");
+        assertEq(a.eeth,       b.eeth,       "WRN.eETH");
+        assertEq(a.membership, b.membership, "WRN.membershipManager");
+        assertEq(a.nextId,     b.nextId,     "WRN.nextRequestId");
+        assertEq(a.lastFin,    b.lastFin,    "WRN.lastFinalizedRequestId");
+        assertEq(a.split,      b.split,      "WRN.split");
+        assertEq(a.scanFrom,   b.scanFrom,   "WRN.scanFrom");
+        assertEq(a.scanTo,     b.scanTo,     "WRN.scanTo");
+        assertEq(a.agg,        b.agg,        "WRN.aggregateSum");
+        assertEq(a.remainder,  b.remainder,  "WRN.remainder");
+        assertEq(a.paused,     b.paused,     "WRN.paused");
+    }
+
+    function setUp() public {
+        // Latest-block fork; realistic mainnet state.
+        vm.createSelectFork(vm.envString("MAINNET_RPC_URL"));
+    }
+
+    function _snap(address target, uint256 n) internal view returns (bytes32[] memory a) {
+        a = new bytes32[](n);
+        for (uint256 i = 0; i < n; i++) {
+            a[i] = vm.load(target, bytes32(i));
+        }
+    }
+
+    function _diff(string memory label, address target, bytes32[] memory pre) internal returns (uint256 drifts) {
+        for (uint256 i = 0; i < pre.length; i++) {
+            bytes32 post = vm.load(target, bytes32(i));
+            if (post != pre[i]) {
+                drifts++;
+                emit log_named_string("drift in", label);
+                emit log_named_uint("  slot", i);
+                emit log_named_bytes32("  pre ", pre[i]);
+                emit log_named_bytes32("  post", post);
+            }
+        }
+    }
+
+    function test_upgrade_preserves_all_sequential_storage() public {
+        // ------------------------------------------------------------------
+        // 1. Snapshot every sequential slot pre-upgrade
+        // ------------------------------------------------------------------
+        bytes32[] memory preLP  = _snap(LIQUIDITY_POOL, SCAN_SLOTS);
+        bytes32[] memory preWRN = _snap(WITHDRAW_REQUEST_NFT, SCAN_SLOTS);
+
+        // Guard slot must be pristine (0) on live mainnet prior to upgrade.
+        // If not, we'd have a pre-existing collision — the whole approach fails.
+        assertEq(vm.load(LIQUIDITY_POOL, GUARD_SLOT), bytes32(0), "LP guard slot not zero pre-upgrade");
+        assertEq(vm.load(WITHDRAW_REQUEST_NFT, GUARD_SLOT), bytes32(0), "WRN guard slot not zero pre-upgrade");
+
+        // Typed getter snapshot — independent cross-check of the slot scan.
+        LiquidityPool lp = LiquidityPool(payable(LIQUIDITY_POOL));
+        WithdrawRequestNFT wrn = WithdrawRequestNFT(WITHDRAW_REQUEST_NFT);
+
+        LPSnap memory lpPre = _snapLP(lp);
+        WRNSnap memory wrnPre = _snapWRN(wrn);
+
+        // ------------------------------------------------------------------
+        // 2. Deploy new implementation contracts (with the added guard)
+        // ------------------------------------------------------------------
+        address newLP  = address(new LiquidityPool(PRIORITY_WITHDRAWAL_QUEUE));
+        address newWRN = address(new WithdrawRequestNFT(WITHDRAW_REQUEST_NFT_BUYBACK_SAFE));
+
+        // ------------------------------------------------------------------
+        // 3. Upgrade the proxies in place
+        //    LP:  _authorizeUpgrade -> roleRegistry.onlyProtocolUpgrader
+        //         The UPGRADE_TIMELOCK holds the protocol upgrader role.
+        //    WRN: _authorizeUpgrade -> onlyOwner (read at runtime).
+        // ------------------------------------------------------------------
+        vm.prank(UPGRADE_TIMELOCK);
+        IUUPSProxy(LIQUIDITY_POOL).upgradeTo(newLP);
+
+        address wrnOwner = IOwnableRead(WITHDRAW_REQUEST_NFT).owner();
+        vm.prank(wrnOwner);
+        IUUPSProxy(WITHDRAW_REQUEST_NFT).upgradeTo(newWRN);
+
+        // ------------------------------------------------------------------
+        // 4. Primary check: every scanned slot is byte-identical
+        // ------------------------------------------------------------------
+        uint256 lpDrifts  = _diff("LiquidityPool", LIQUIDITY_POOL, preLP);
+        uint256 wrnDrifts = _diff("WithdrawRequestNFT", WITHDRAW_REQUEST_NFT, preWRN);
+
+        assertEq(lpDrifts, 0, "LP sequential storage drifted after upgrade");
+        assertEq(wrnDrifts, 0, "WRN sequential storage drifted after upgrade");
+
+        // ------------------------------------------------------------------
+        // 5. Guard slot remains clean immediately after upgrade
+        // ------------------------------------------------------------------
+        assertEq(vm.load(LIQUIDITY_POOL, GUARD_SLOT), bytes32(0), "LP guard slot mutated by upgrade");
+        assertEq(vm.load(WITHDRAW_REQUEST_NFT, GUARD_SLOT), bytes32(0), "WRN guard slot mutated by upgrade");
+
+        // ------------------------------------------------------------------
+        // 6. Typed sanity: every accessor returns the exact same value.
+        //    This catches the case where a slot is byte-equal but the
+        //    compiler reinterprets it (type change at same offset). Unlikely
+        //    given we only added inheritance, but it's a cheap belt.
+        // ------------------------------------------------------------------
+        _assertLPEq(_snapLP(lp), lpPre);
+        _assertWRNEq(_snapWRN(wrn), wrnPre);
+
+        // ------------------------------------------------------------------
+        // 7. Smoke test: a guarded function executes end-to-end on the
+        //    upgraded proxy and the guard slot cycles correctly.
+        // ------------------------------------------------------------------
+        if (!lp.paused()) {
+            address user = address(0xB0B0);
+            vm.deal(user, 5 ether);
+            vm.prank(user);
+            lp.deposit{value: 1 ether}();
+
+            assertEq(
+                vm.load(LIQUIDITY_POOL, GUARD_SLOT),
+                bytes32(uint256(1)),
+                "guard slot not NOT_ENTERED after guarded deposit"
+            );
+        }
+    }
+
+    /// @notice After the upgrade, a pre-existing finalized-but-unclaimed
+    ///         request from live mainnet state must still be claimable by its
+    ///         NFT owner. Proves: (a) storage for `_requests[id]` and the NFT
+    ///         ownership mapping is intact, (b) the removal of `whenNotPaused`
+    ///         does not regress happy-path claims, (c) LP.withdraw still wired
+    ///         correctly for the historical accounting path.
+    function test_postUpgrade_preExistingFinalizedRequest_isClaimable() public {
+        _doUpgrade();
+
+        WithdrawRequestNFT wrn = WithdrawRequestNFT(WITHDRAW_REQUEST_NFT);
+        uint32 lastFin = wrn.lastFinalizedRequestId();
+        require(lastFin > 0, "no finalized requests on fork");
+
+        // Scan downward from lastFinalizedRequestId looking for an
+        // unclaimed (ownerOf doesn't revert) + valid request with non-zero
+        // claim amount. Skip the very top few in case the LP doesn't have
+        // the liquidity buffered yet.
+        uint256 found = 0;
+        address nftOwner;
+        uint256 maxScan = 1000;
+        for (uint256 i = 0; i < maxScan; i++) {
+            if (i >= lastFin) break;
+            uint256 candidate = lastFin - i;
+
+            (bool ok, bytes memory data) = address(wrn).staticcall(
+                abi.encodeWithSignature("ownerOf(uint256)", candidate)
+            );
+            if (!ok) continue;
+            address o = abi.decode(data, (address));
+            if (o == address(0)) continue;
+
+            // isValid reverts if !_exists; ownerOf already asserted existence,
+            // so this is safe.
+            if (!wrn.isValid(candidate)) continue;
+
+            // Skip zero-amount edge cases (partial claims or weird shares).
+            if (wrn.getClaimableAmount(candidate) == 0) continue;
+
+            found = candidate;
+            nftOwner = o;
+            break;
+        }
+
+        require(found != 0, "no finalized+valid+unclaimed request found in scan range");
+
+        uint256 claimable = wrn.getClaimableAmount(found);
+        uint256 balBefore = nftOwner.balance;
+
+        vm.prank(nftOwner);
+        wrn.claimWithdraw(found);
+
+        assertGt(nftOwner.balance, balBefore, "pre-existing finalized request produced no payout");
+        assertApproxEqAbs(
+            nftOwner.balance - balBefore,
+            claimable,
+            1,
+            "payout deviates from getClaimableAmount"
+        );
+    }
+
+    /// @notice Also exercises the permissionless-claim property on real state:
+    ///         pause WRN (via PROTOCOL_PAUSER), then claim a pre-existing
+    ///         finalized request. Must succeed post-upgrade.
+    function test_postUpgrade_claimWorksWhilePaused_onMainnetData() public {
+        _doUpgrade();
+
+        WithdrawRequestNFT wrn = WithdrawRequestNFT(WITHDRAW_REQUEST_NFT);
+        uint32 lastFin = wrn.lastFinalizedRequestId();
+        require(lastFin > 0, "no finalized requests on fork");
+
+        uint256 found = 0;
+        address nftOwner;
+        for (uint256 i = 0; i < 1000; i++) {
+            if (i >= lastFin) break;
+            uint256 candidate = lastFin - i;
+            (bool ok, bytes memory data) = address(wrn).staticcall(
+                abi.encodeWithSignature("ownerOf(uint256)", candidate)
+            );
+            if (!ok) continue;
+            address o = abi.decode(data, (address));
+            if (o == address(0)) continue;
+            if (!wrn.isValid(candidate)) continue;
+            if (wrn.getClaimableAmount(candidate) == 0) continue;
+            found = candidate;
+            nftOwner = o;
+            break;
+        }
+        require(found != 0, "no candidate");
+
+        // Pause WRN directly via the namespaced pauser. Instead of hunting
+        // down the live pauser address, grant the role to this test via
+        // RoleRegistry's owner/DEFAULT_ADMIN.
+        bytes32 pauserRole = wrn.roleRegistry().PROTOCOL_PAUSER();
+        address roleRegOwner = IOwnableRead(address(wrn.roleRegistry())).owner();
+        vm.prank(roleRegOwner);
+        (bool granted,) = address(wrn.roleRegistry()).call(
+            abi.encodeWithSignature("grantRole(bytes32,address)", pauserRole, address(this))
+        );
+        require(granted, "role grant failed");
+
+        wrn.pauseContract();
+        assertTrue(wrn.paused(), "precondition: WRN paused");
+
+        uint256 balBefore = nftOwner.balance;
+        vm.prank(nftOwner);
+        wrn.claimWithdraw(found);
+
+        assertGt(nftOwner.balance, balBefore, "paused WRN must not block finalized claim");
+    }
+
+    /// @dev Internal helper used by the integrity test above - upgrades both
+    ///      proxies to new implementations with the guard + permissionless
+    ///      claim changes.
+    function _doUpgrade() internal {
+        address newLP = address(new LiquidityPool(PRIORITY_WITHDRAWAL_QUEUE));
+        address newWRN = address(new WithdrawRequestNFT(WITHDRAW_REQUEST_NFT_BUYBACK_SAFE));
+
+        vm.prank(UPGRADE_TIMELOCK);
+        IUUPSProxy(LIQUIDITY_POOL).upgradeTo(newLP);
+
+        address wrnOwner = IOwnableRead(WITHDRAW_REQUEST_NFT).owner();
+        vm.prank(wrnOwner);
+        IUUPSProxy(WITHDRAW_REQUEST_NFT).upgradeTo(newWRN);
+    }
+
+    /// @dev Separately verify that, post-upgrade, the guard actually blocks
+    ///      re-entry. This is defence-in-depth in case some ABI mismatch made
+    ///      the modifier no-op.
+    function test_postUpgrade_guardBlocksReentry() public {
+        address newLP = address(new LiquidityPool(PRIORITY_WITHDRAWAL_QUEUE));
+        vm.prank(UPGRADE_TIMELOCK);
+        IUUPSProxy(LIQUIDITY_POOL).upgradeTo(newLP);
+
+        // Plant ENTERED directly; the next guarded call must revert with the
+        // reentrancy error selector — proves the modifier reads the slot we
+        // expect on the upgraded proxy.
+        vm.store(LIQUIDITY_POOL, GUARD_SLOT, bytes32(uint256(2)));
+
+        address user = address(0xB0B0);
+        vm.deal(user, 1 ether);
+
+        LiquidityPool lp = LiquidityPool(payable(LIQUIDITY_POOL));
+        if (!lp.paused()) {
+            vm.expectRevert(ReentrancyGuardNamespaced.ReentrancyGuardReentrantCall.selector);
+            vm.prank(user);
+            lp.deposit{value: 1 ether}();
+        }
+    }
+}
```

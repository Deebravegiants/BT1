### Title
Immutable `i_maxSupply` Cap in `WrappedRSETH` Permanently Blocks CCIP Yield Delivery When Supply Is Exhausted - (File: `contracts/ccip/WrappedRSETH.sol`)

---

### Summary

`WrappedRSETH` enforces an immutable maximum supply (`i_maxSupply`) set at deployment. When `totalSupply()` reaches this cap, any CCIP bridge call to `mint()` reverts with `MaxSupplyExceeded`. Because `i_maxSupply` is `immutable` and no admin function exists to raise it, the cap is permanent. Any in-flight CCIP message whose execution triggers `mint()` will fail irreversibly, permanently freezing the bridged yield for affected recipients.

---

### Finding Description

`WrappedRSETH` is the Chainlink CCIP burn/mint token on L2. It implements `IBurnMintERC20`, the interface CCIP token pools use to mint tokens upon message delivery. The `mint()` function enforces a hard cap:

```solidity
// contracts/ccip/WrappedRSETH.sol, line 138
if (i_maxSupply != 0 && totalSupply() + amount > i_maxSupply) revert MaxSupplyExceeded(totalSupply() + amount);
```

`i_maxSupply` is declared `immutable` and assigned once in the constructor:

```solidity
// contracts/ccip/WrappedRSETH.sol, lines 41, 54
uint256 internal immutable i_maxSupply;
...
i_maxSupply = maxSupply_;
```

There is no setter, no upgrade path, and no admin function to increase `i_maxSupply` after deployment. The contract comment explicitly states: *"The total supply can be limited during deployment."*

On L1, `L1VaultV2.bridgeRsETHToL2UsingCCIP()` locks rsETH and sends a CCIP message targeting `WrappedRSETH` on L2. The CCIP token pool on L2 calls `WrappedRSETH.mint(recipient, amount)` to complete delivery. If `totalSupply()` is at `i_maxSupply` when this call executes, the mint reverts, the CCIP message execution fails, and — because `i_maxSupply` cannot be raised — no retry will ever succeed.

---

### Impact Explanation

**Permanent freezing of unclaimed yield.** Once `totalSupply()` reaches `i_maxSupply`:

- Every subsequent CCIP delivery attempt reverts with `MaxSupplyExceeded`.
- The L1 rsETH is already committed to the CCIP bridge (locked or burned in the token pool).
- `i_maxSupply` is `immutable` — no owner, admin, or governance action can raise it.
- CCIP manual execution retries will also revert for the same reason.
- Affected users permanently lose access to their bridged yield.

This matches the allowed impact: **Medium — Permanent freezing of unclaimed yield**.

---

### Likelihood Explanation

The precondition is that `WrappedRSETH` is deployed with a finite `maxSupply_` (i.e., `maxSupply_ > 0`). The contract explicitly supports this configuration and the constructor accepts it without restriction. Once deployed with a finite cap, the scenario requires only that organic bridging activity fills `totalSupply()` to `i_maxSupply` — no attacker action is needed. The likelihood is **medium**: it depends on the deployment parameter choice, but the contract design makes it a supported and reachable state.

---

### Recommendation

1. **Remove the supply cap entirely** if `WrappedRSETH` is intended to serve as an unbounded CCIP bridge token. Deploy with `maxSupply_ = 0`.
2. **If a cap is required**, replace `immutable i_maxSupply` with a mutable state variable and add an owner-restricted setter so the cap can be raised if supply pressure demands it:
   ```solidity
   uint256 internal s_maxSupply;
   function setMaxSupply(uint256 newMax) external onlyOwner { s_maxSupply = newMax; }
   ```
3. **Add a CCIP message recovery path**: implement a fallback that, on `MaxSupplyExceeded`, holds the pending mint in escrow so it can be retried after the cap is raised.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/ccip/WrappedRSETH.sol";

contract MaxSupplyPoC is Test {
    WrappedRSETH token;
    address owner   = address(0xA);
    address minter  = address(0xB); // simulates CCIP token pool
    address user    = address(0xC);
    address yield_r = address(0xD); // yield recipient

    function setUp() public {
        vm.prank(owner);
        // Deploy with maxSupply = 1000e18
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, 1000e18, owner);

        vm.prank(owner);
        token.grantMintRole(minter);
    }

    function test_maxSupplyBlocksCCIPYieldDelivery() public {
        // Step 1: Fill supply to cap via normal bridging
        vm.prank(minter);
        token.mint(user, 1000e18); // totalSupply == i_maxSupply

        assertEq(token.totalSupply(), 1000e18);

        // Step 2: CCIP bridge attempts to deliver 1 wei of yield
        vm.prank(minter);
        vm.expectRevert(
            abi.encodeWithSelector(WrappedRSETH.MaxSupplyExceeded.selector, 1000e18 + 1)
        );
        token.mint(yield_r, 1); // reverts — yield permanently frozen

        // Step 3: Confirm no recovery path — i_maxSupply is immutable
        assertEq(token.maxSupply(), 1000e18); // cannot be raised
    }
}
```

**Expected result:** `mint(yield_r, 1)` reverts with `MaxSupplyExceeded(1000000000000000000001)`. No function exists to raise `i_maxSupply`. The yield recipient permanently cannot receive their tokens. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L41-54)
```text
    uint256 internal immutable i_maxSupply;

    constructor(
        string memory name,
        string memory symbol,
        uint8 decimals_,
        uint256 maxSupply_,
        address _owner
    )
        ERC677(name, symbol)
        ConfirmedOwnerWithProposal(_owner, address(0))
    {
        i_decimals = decimals_;
        i_maxSupply = maxSupply_;
```

**File:** contracts/ccip/WrappedRSETH.sol (L137-141)
```text
    function mint(address account, uint256 amount) external override onlyMinter validAddress(account) {
        if (i_maxSupply != 0 && totalSupply() + amount > i_maxSupply) revert MaxSupplyExceeded(totalSupply() + amount);

        _mint(account, amount);
    }
```

**File:** contracts/ccip/IBurnMintERC20.sol (L6-12)
```text
interface IBurnMintERC20 is IERC20 {
    /// @notice Mints new tokens for a given address.
    /// @param account The address to mint the new tokens to.
    /// @param amount The number of tokens to be minted.
    /// @dev this function increases the total supply.
    function mint(address account, uint256 amount) external;

```

**File:** contracts/L1VaultV2.sol (L341-367)
```text
    function bridgeRsETHToL2UsingCCIP(uint256 amount) external payable nonReentrant onlyRole(MANAGER_ROLE) {
        if (bridgeType != BridgeType.CCIP) {
            revert InactiveBridgeType();
        }

        if (rsETH.balanceOf(address(this)) < amount) {
            revert InsufficientRsETHBalance();
        }

        if (amount == 0) {
            revert ZeroAmount();
        }

        uint256 fee = getCCIPFee(amount);

        if (msg.value != fee) {
            revert IncorrectCCIPFee();
        }

        IERC20(address(rsETH)).safeIncreaseAllowance(address(ccipRouter), amount);

        Client.EVM2AnyMessage memory message = getCCIPMessage(amount);

        bytes32 messageId = ccipRouter.ccipSend{ value: msg.value }(destinationChainSelector, message);

        emit BridgedRsETHToL2UsingCCIP(destinationChainSelector, l2Receiver, amount, messageId);
    }
```

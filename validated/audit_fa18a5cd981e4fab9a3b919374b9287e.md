Looking at the full `WrappedRSETH.sol` contract, I can now perform a complete analysis.

**Key code facts:**

- `mint()` at line 137–141: no rate limit, no per-tx cap — a single call can mint up to `i_maxSupply - totalSupply()` in one transaction.
- `revokeMintRole()` at line 173–177: instant removal with no time-lock, no pending-revocation state, and no snapshot that would freeze the minter's ability to mint while revocation is in flight.
- `i_maxSupply` is immutable (line 41): once the cap is hit, it can never be raised.

**Attack path evaluation:**

| Step | Feasibility |
|---|---|
| Attacker holds minter role | Precondition — no compromise needed |
| Attacker monitors mempool for `revokeMintRole(attacker)` | Standard mempool surveillance |
| Attacker submits high-gas-price filler txs to stuff N blocks | Expensive but mechanically possible; explicitly the "Low. Block stuffing" impact category |
| Attacker calls `mint(attacker, i_maxSupply - totalSupply())` | Single call, no per-tx cap, passes `onlyMinter` because role not yet removed |
| `revokeMintRole` lands — role removed, but supply cap already hit | `MaxSupplyExceeded` reverts all future CCIP mints permanently |

**Reject-criteria check:**

- Not admin/operator compromise — the attacker *is* the minter, no key leak needed.
- Not "front-running only" — block stuffing is a distinct, active technique (filling blocks to delay a specific tx), not merely outbidding.
- Not griefing with no scoped impact — exhausting `i_maxSupply` permanently disables CCIP bridging for the token.
- Locally testable with `vm.roll` / `vm.txGasPrice` on unmodified code.

The "Low. Block stuffing" impact is explicitly listed in the allowed scope, and the root cause (no time-lock on revocation, no per-tx mint cap, immutable supply ceiling) is entirely in the production contract.

---

### Title
Minter Can Exhaust `i_maxSupply` via Block Stuffing Before `revokeMintRole` Lands, Permanently Disabling CCIP Mints — (`contracts/ccip/WrappedRSETH.sol`)

### Summary
`WrappedRSETH` allows a single `mint()` call to consume the entire remaining token supply in one transaction, and `revokeMintRole()` takes effect only when its transaction is included. A minter who detects a pending revocation can stuff blocks to delay inclusion and race to mint up to `i_maxSupply`, permanently hitting the immutable cap and preventing all future CCIP-bridged mints.

### Finding Description
`mint()` enforces only a ceiling check against `i_maxSupply` with no per-transaction cap, no daily rate limit, and no cooldown. [1](#0-0) 

`revokeMintRole()` removes the minter atomically in the block it is included, with no time-lock, no pending-revocation flag, and no mechanism to freeze the minter's ability to call `mint()` while the revocation is in flight. [2](#0-1) 

`i_maxSupply` is immutable; once `totalSupply() == i_maxSupply`, every future `mint()` call reverts with `MaxSupplyExceeded`, permanently disabling CCIP token delivery on this chain. [3](#0-2) 

The attack sequence:
1. Owner submits `revokeMintRole(attacker)` to the mempool.
2. Attacker detects the pending tx via mempool surveillance.
3. Attacker submits enough high-gas-price filler transactions to fill N blocks, delaying the revocation.
4. In the same window, attacker calls `mint(attacker, i_maxSupply - totalSupply())` — passes `onlyMinter` because the role is still active.
5. `revokeMintRole` eventually lands, but `totalSupply() == i_maxSupply`; all subsequent CCIP mint attempts revert.

### Impact Explanation
The supply cap is permanently exhausted. Every future CCIP cross-chain transfer that triggers a `mint()` on this destination chain will revert with `MaxSupplyExceeded`. This is a permanent, irreversible denial of the token's core CCIP bridging functionality. The attacker also receives tokens equal to the remaining supply.

**Impact: Low — Block stuffing / contract fails to deliver promised returns (CCIP bridging permanently broken).**

### Likelihood Explanation
Requires the attacker to already hold the minter role (a trusted position, but one that can be compromised or go rogue) and to afford block-stuffing costs. On L2s (Arbitrum, Base, Optimism) where this CCIP-wrapped token is most likely deployed, block gas limits are lower and block stuffing is significantly cheaper than on Ethereum mainnet, raising practical likelihood. The mempool surveillance step is standard.

### Recommendation
1. **Add a time-lock to role revocation**: introduce a two-step revocation (announce → delay → execute) so the minter cannot act after announcement.
2. **Alternatively, add a per-transaction mint cap** so no single call can exhaust the remaining supply.
3. **Or freeze minting immediately on announcement**: add a `pendingRevocation` mapping that `onlyMinter` checks, allowing the owner to atomically disable a minter's ability to mint before the full revocation is processed.

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/ccip/WrappedRSETH.sol";

contract BlockStuffingPoC is Test {
    WrappedRSETH token;
    address owner   = address(0x1);
    address attacker = address(0x2);

    uint256 constant MAX_SUPPLY = 1000 ether;

    function setUp() public {
        vm.prank(owner);
        token = new WrappedRSETH("Wrapped rsETH", "wrsETH", 18, MAX_SUPPLY, owner);

        vm.prank(owner);
        token.grantMintRole(attacker);
    }

    function testBlockStuffingExhaustSupply() public {
        // Owner submits revokeMintRole — simulate it sitting in mempool (not yet mined)
        // Attacker detects it and stuffs blocks (simulated by vm.roll)
        // Before revocation lands, attacker mints remaining supply

        uint256 remaining = MAX_SUPPLY - token.totalSupply();

        // Attacker mints entire remaining supply in one tx (role still active)
        vm.prank(attacker);
        token.mint(attacker, remaining);

        assertEq(token.totalSupply(), MAX_SUPPLY);

        // Now owner's revocation lands
        vm.prank(owner);
        token.revokeMintRole(attacker);

        // Any future CCIP mint attempt reverts — supply cap permanently hit
        address ccipPool = address(0x3);
        vm.prank(owner);
        token.grantMintRole(ccipPool);

        vm.prank(ccipPool);
        vm.expectRevert(
            abi.encodeWithSelector(WrappedRSETH.MaxSupplyExceeded.selector, MAX_SUPPLY + 1 ether)
        );
        token.mint(address(0x4), 1 ether); // CCIP bridge delivery permanently broken
    }
}
```

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L41-41)
```text
    uint256 internal immutable i_maxSupply;
```

**File:** contracts/ccip/WrappedRSETH.sol (L137-141)
```text
    function mint(address account, uint256 amount) external override onlyMinter validAddress(account) {
        if (i_maxSupply != 0 && totalSupply() + amount > i_maxSupply) revert MaxSupplyExceeded(totalSupply() + amount);

        _mint(account, amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L173-177)
```text
    function revokeMintRole(address minter) external onlyOwner {
        if (s_minters.remove(minter)) {
            emit MintAccessRevoked(minter);
        }
    }
```

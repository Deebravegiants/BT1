### Title
Unguarded `token = address(0)` Initialization Allows Temporary Freezing of Distributed Funds — (`contracts/utils/MerkleDistributor/MerkleDistributor.sol`)

---

### Summary

`initialize()` explicitly permits `token_ = address(0)` (the comment even documents this as intentional). However, neither `setMerkleRoot()` nor `claim()` guards against `token == address(0)`. If a merkle root is set before `setToken()` is called, every `claim()` invocation reverts at the `safeTransfer` call, temporarily freezing any tokens already deposited in the contract.

---

### Finding Description

`initialize()` skips the zero-address check for `token_`: [1](#0-0) 

The comment `// token can be set later but not the protocol treasury` confirms this is an intended deployment path. `setMerkleRoot()` has no guard requiring `token != address(0)`: [2](#0-1) 

`claim()` proceeds through all validation (merkle proof, index, duplicate checks) and then unconditionally calls: [3](#0-2) 

`IERC20(address(0)).safeTransfer(...)` reverts because `address(0)` has no code. OpenZeppelin's `SafeERC20` uses `Address.functionCall`, which checks `isContract` and reverts on a zero address.

**Reachable call sequence (no privilege escalation required):**
1. `initialize(address(0), treasury, fee)` — owner deploys with `token = address(0)` (explicitly allowed)
2. `IERC20(realToken).transfer(distributor, amount)` — tokens deposited into the contract
3. `setMerkleRoot(root)` — owner sets a valid root (no token check)
4. `claim(index, account, amount, proof)` — **reverts** at `IERC20(address(0)).safeTransfer`
5. Funds remain frozen until owner calls `setToken(realToken)`

---

### Impact Explanation

Tokens deposited into the distributor are unclaimable for the entire window between `setMerkleRoot()` and `setToken()`. This matches **Medium — Temporary freezing of funds**. The deployer can resolve it by calling `setToken()`, but until then all legitimate claimants are blocked and their entitled tokens are locked in the contract.

---

### Likelihood Explanation

The contract explicitly documents and supports `token = address(0)` at deploy time. A deployer following the natural setup sequence (deploy → fund → set root → open claims) who forgets to call `setToken()` first triggers this state. No attacker action is required; the deployer's own intended workflow is the trigger.

---

### Recommendation

Add a zero-address check for `token` in `setMerkleRoot()`:

```solidity
function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
    if (_merkleRootToSet == bytes32(0)) revert ZeroValueProvided();
+   if (token == address(0)) revert ZeroValueProvided(); // token must be set before activating claims
    ...
}
```

Alternatively, add the same guard at the top of `claim()` to produce a clear error instead of a cryptic revert.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/utils/MerkleDistributor/MerkleDistributor.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockToken is ERC20 {
    constructor() ERC20("T", "T") { _mint(msg.sender, 1e24); }
}

contract MerkleDistributorTest is Test {
    MerkleDistributor dist;
    MockToken token;

    function setUp() public {
        dist = new MerkleDistributor();
        token = new MockToken();
    }

    function testTemporaryFreeze() public {
        address treasury = address(0xBEEF);

        // 1. Deploy with token = address(0)
        dist.initialize(address(0), treasury, 0);

        // 2. Fund the distributor with real tokens
        token.transfer(address(dist), 1000e18);

        // 3. Build a trivial merkle tree for one leaf
        address user = address(0xCAFE);
        uint256 index = 1;
        uint256 amount = 100e18;
        bytes32 leaf = keccak256(abi.encodePacked(index, user, amount));
        bytes32[] memory proof = new bytes32[](0); // single-leaf tree: root == leaf

        // 4. Set merkle root (no token check)
        dist.setMerkleRoot(leaf);

        // 5. claim() reverts — tokens are frozen
        vm.expectRevert();
        dist.claim(index, user, amount, proof);

        // 6. Owner fixes it by calling setToken
        dist.setToken(address(token));

        // 7. claim() now succeeds
        dist.claim(index, user, amount, proof);
        assertEq(token.balanceOf(user), 100e18);
    }
}
```

### Citations

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L71-87)
```text
    function initialize(address token_, address _protocolTreasury, uint256 _feeInBPS) external initializer {
        // token can be set later but not the protocol treasury
        if (_protocolTreasury == address(0)) {
            revert ZeroValueProvided();
        }

        if (_feeInBPS > MAX_FEE_IN_BPS) {
            revert InvalidFeeInBPS();
        }

        __Ownable_init();
        __Pausable_init();

        token = token_;
        protocolTreasury = _protocolTreasury;
        feeInBPS = _feeInBPS;
    }
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L141-144)
```text
        IERC20(token).safeTransfer(account, amountToSend);

        // Send the fee to the protocol treasury
        IERC20(token).safeTransfer(protocolTreasury, fee);
```

**File:** contracts/utils/MerkleDistributor/MerkleDistributor.sol (L156-167)
```text
    function setMerkleRoot(bytes32 _merkleRootToSet) external onlyOwner {
        if (_merkleRootToSet == bytes32(0)) {
            revert ZeroValueProvided();
        }

        currentMerkleRoot = _merkleRootToSet;

        currentMerkleRootIndex++;
        currentIndex++;

        emit MerkleRootSet(currentMerkleRootIndex, currentMerkleRoot);
    }
```

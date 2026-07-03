The code is fully readable. Let me analyze the logic carefully.

### Title
Per-Token Cap in `depositBridgerAssets` Ignores Aggregate Collateral, Allowing Over-Collateralization — (`contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`depositBridgerAssets` enforces a per-token cap computed as `totalSupply - balance[token]`. With two allowed tokens both starting at zero balance, the BRIDGER_ROLE can deposit up to `totalSupply` of **each** token independently, resulting in aggregate collateral of up to `2 × totalSupply` against a `totalSupply` of wrsETH. The excess collateral is permanently locked with no recovery path.

---

### Finding Description

`maxAmountToDepositBridgerAsset` computes the cap for a single asset in isolation: [1](#0-0) 

```solidity
uint256 wrsETHSupply = totalSupply();
uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));
if (balanceOfAssetInWrapper > wrsETHSupply) return 0;
return wrsETHSupply - balanceOfAssetInWrapper;
```

`depositBridgerAssets` uses this per-token cap as its only guard: [2](#0-1) 

There is no check against the **sum** of all allowed-token balances. The contract supports multiple allowed tokens (added via `addAllowedToken` / `reinitialize`): [3](#0-2) [4](#0-3) 

Concrete sequence with `totalSupply = S`, `balance[tokenA] = 0`, `balance[tokenB] = 0`:

| Step | Call | Cap check | Passes? | New aggregate |
|------|------|-----------|---------|---------------|
| 1 | `depositBridgerAssets(tokenA, S)` | `S - 0 = S ≥ S` | ✓ | S |
| 2 | `depositBridgerAssets(tokenB, S)` | `S - 0 = S ≥ S` | ✓ | **2S** |

After step 2, the contract holds `2S` tokens but only `S` wrsETH exists. The only exit for tokens is `_withdraw`, which burns wrsETH 1:1: [5](#0-4) 

Since only `S` wrsETH can ever be burned, the excess `S` tokens of collateral are permanently irrecoverable — there is no admin sweep or emergency withdrawal function in the contract.

---

### Impact Explanation

The contract fails to enforce its core invariant (`sum(balance[allowedToken]) ≤ totalSupply`). Excess collateral deposited by the BRIDGER_ROLE becomes permanently locked. Users are unaffected (they can still redeem wrsETH 1:1), but the protocol loses the over-deposited collateral with no recovery mechanism. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value** (from the user perspective), though the locked excess represents a real asset loss for the protocol/bridger.

---

### Likelihood Explanation

Requires the BRIDGER_ROLE to call `depositBridgerAssets` for two different allowed tokens. This is a realistic operational scenario: `reinitialize` adds a second allowed token (`_altRsETH`), and the bridger may legitimately attempt to collateralize each token independently up to the full supply. No malicious intent is required — a good-faith bridger following the per-token cap logic would trigger this. [6](#0-5) 

---

### Recommendation

Replace the per-token cap with an aggregate cap. In `maxAmountToDepositBridgerAsset`, subtract the **total balance of all allowed tokens** from `totalSupply`, not just the balance of the queried token. Alternatively, track a single `totalCollateral` storage variable that is incremented on every `depositBridgerAssets` call and checked against `totalSupply()`.

---

### Proof of Concept

```solidity
// Invariant test (local fork or unit test)
// Setup: totalSupply = 100e18, tokenA and tokenB both allowed, both balances = 0

uint256 S = wrapper.totalSupply(); // 100e18

// Step 1: BRIDGER deposits tokenA up to full cap
vm.prank(bridger);
wrapper.depositBridgerAssets(tokenA, S); // passes: cap = S - 0 = S

// Step 2: BRIDGER deposits tokenB up to full cap
vm.prank(bridger);
wrapper.depositBridgerAssets(tokenB, S); // passes: cap = S - 0 = S (tokenB balance still 0)

// Invariant violated:
uint256 totalCollateral = IERC20(tokenA).balanceOf(address(wrapper))
                        + IERC20(tokenB).balanceOf(address(wrapper));
assert(totalCollateral <= wrapper.totalSupply()); // FAILS: 2S > S
```

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L24-24)
```text
    mapping(address allowedToken => bool isAllowed) public allowedTokens;
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L99-110)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L162-170)
```text
    function depositBridgerAssets(address _asset, uint256 _amount) external onlyRole(BRIDGER_ROLE) {
        if (maxAmountToDepositBridgerAsset(_asset) < _amount) {
            revert CannotDeposit();
        }

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        emit BridgerDeposited(_asset, msg.sender, _amount);
    }
```

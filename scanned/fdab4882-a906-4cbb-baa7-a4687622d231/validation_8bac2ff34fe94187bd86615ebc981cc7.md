### Title
No Way to Invalidate Issued Permits in AGETHTokenWrapper - (File: contracts/agETH/AGETHTokenWrapper.sol)

### Summary
`AGETHTokenWrapper` inherits `ERC20PermitUpgradeable` but exposes no mechanism for a token holder to invalidate an outstanding EIP-2612 permit by incrementing their own nonce. A permit signed with a long-dated deadline cannot be revoked, allowing an attacker who holds such a permit to front-run any on-chain approval revocation and subsequently drain the victim's wrapped agETH balance.

### Finding Description
`AGETHTokenWrapper` is an upgradeable ERC-20 wrapper for alternative agETH tokens on L2 chains. It inherits `ERC20PermitUpgradeable` from OpenZeppelin v4.9.0, which adds the standard `permit()` function for gasless, signature-based approvals. [1](#0-0) 

The inherited `ERC20PermitUpgradeable` stores per-user nonces in a private `CountersUpgradeable.Counter` mapping and exposes only an `internal` `_useNonce()` helper. [2](#0-1) [3](#0-2) 

Because `_useNonce` is `internal` and `AGETHTokenWrapper` adds no public wrapper around it, there is no way for a user to self-increment their nonce and thereby invalidate a previously signed permit. The only way the nonce advances is when a permit is actually consumed.

The `withdraw` / `withdrawTo` functions burn the **caller's** balance and return the underlying altAgETH token 1:1. [4](#0-3) 

This means that once an attacker has obtained the victim's agETH wrapper tokens via `transferFrom` (enabled by the permit), they can immediately call `withdraw` to redeem the underlying altAgETH asset.

### Impact Explanation
**Critical — Direct theft of user funds.**

An attacker who holds a valid, long-dated permit can:
1. Wait for the victim to attempt revocation via `approve(attacker, 0)`.
2. Front-run that transaction by submitting the permit, restoring the allowance.
3. Call `transferFrom` to move the victim's agETH wrapper tokens.
4. Call `withdraw` to redeem the underlying altAgETH tokens.

The victim loses their entire wrapped agETH balance with no recourse.

### Likelihood Explanation
**Medium.** Permits are a standard DeFi primitive. Users routinely sign permits for DEX routers, lending protocols, and other integrations. A permit signed with `deadline = type(uint256).max` (common in many UIs) is permanently valid until consumed. If the user later distrusts the spender (e.g., after a protocol compromise or a change of mind), they have no on-chain escape hatch.

### Recommendation
Add a public `increaseNonce()` function that calls `_useNonce` on behalf of `msg.sender`, mirroring the fix applied in the referenced eBTC report:

```solidity
/// @notice Invalidates all outstanding permits for the caller by advancing their nonce.
function increaseNonce() external returns (uint256) {
    return _useNonce(msg.sender);
}
```

This allows any user to atomically burn all outstanding signed permits without relying on the deadline.

### Proof of Concept

```
Setup:
  - victim holds 100 agETH wrapper tokens
  - victim signs permit(owner=victim, spender=attacker, value=100, deadline=type(uint256).max, ...)

Attack:
  1. victim broadcasts approve(attacker, 0)          // attempt to revoke
  2. attacker front-runs with permit(...)             // nonce consumed, allowance = 100
  3. attacker calls transferFrom(victim, attacker, 100)
  4. attacker calls withdraw(altAgETH, 100)           // burns attacker's 100 wrapper tokens
                                                      // receives 100 altAgETH
  Result: victim loses 100 altAgETH worth of value
``` [5](#0-4) [6](#0-5)

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L1-17)
```text
// SPDX-License-Identifier: UNLICENSED
pragma solidity 0.8.27;

import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import {
    ERC20PermitUpgradeable
} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20PermitUpgradeable.sol";
import { ERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/ERC20Upgradeable.sol";
import { SafeERC20Upgradeable } from "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";

/// @title AGETHTokenWrapper
/// @notice This contract is a wrapper for alternative agETH tokens in L2 chains for a canonical agETH token from Kelp
/// @dev It is an upgradeable ERC20 token that wraps an alternative agETH token
/// @dev It also uses the ERC20PermitUpgradeable extension
/// @dev The alt agETH tokens can be swapped 1:1 for the canonical agETH token
contract AGETHTokenWrapper is Initializable, AccessControlUpgradeable, ERC20Upgradeable, ERC20PermitUpgradeable {
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L45-55)
```text
    function initialize(address admin, address manager, address _altAgETH) external initializer {
        __ERC20_init("agETHWrapper", "agETH");
        __ERC20Permit_init("agETHWrapper");
        __AccessControl_init();

        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(MANAGER_ROLE, manager);
        _setupRole(BRIDGER_ROLE, manager);

        allowedTokens[_altAgETH] = true;
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-119)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20PermitUpgradeable.sol (L25-30)
```text
abstract contract ERC20PermitUpgradeable is Initializable, ERC20Upgradeable, IERC20PermitUpgradeable, EIP712Upgradeable {
    using CountersUpgradeable for CountersUpgradeable.Counter;

    mapping(address => CountersUpgradeable.Counter) private _nonces;

    // solhint-disable-next-line var-name-mixedcase
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20PermitUpgradeable.sol (L56-75)
```text
    function permit(
        address owner,
        address spender,
        uint256 value,
        uint256 deadline,
        uint8 v,
        bytes32 r,
        bytes32 s
    ) public virtual override {
        require(block.timestamp <= deadline, "ERC20Permit: expired deadline");

        bytes32 structHash = keccak256(abi.encode(_PERMIT_TYPEHASH, owner, spender, value, _useNonce(owner), deadline));

        bytes32 hash = _hashTypedDataV4(structHash);

        address signer = ECDSAUpgradeable.recover(hash, v, r, s);
        require(signer == owner, "ERC20Permit: invalid signature");

        _approve(owner, spender, value);
    }
```

**File:** lib/openzeppelin-contracts-upgradeable/contracts/token/ERC20/extensions/ERC20PermitUpgradeable.sol (L97-101)
```text
    function _useNonce(address owner) internal virtual returns (uint256 current) {
        CountersUpgradeable.Counter storage nonce = _nonces[owner];
        current = nonce.current();
        nonce.increment();
    }
```

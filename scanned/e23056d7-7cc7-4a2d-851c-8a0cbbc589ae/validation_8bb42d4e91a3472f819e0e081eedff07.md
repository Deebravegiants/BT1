### Title
Blacklisted pool can self-clear its oracle blacklist via permissionless `register()` — (`smart-contracts-poc/contracts/oracles/providers/OracleBase.sol`)

---

### Summary

`OracleBase.register()` is a permissionless, payable function that explicitly removes a pool from the blacklist as a side-effect of registration. Because the default `registrationFee` is 1 wei and any caller can invoke `register()` for any valid pool, a pool that has been blacklisted by the admin can trivially re-register and clear its own blacklist status, bypassing the admin's enforcement.

---

### Finding Description

The `OracleBase` contract maintains a `mapping(address => bool) public blacklisted` and enforces it in the `price()` oracle read path used by pools during swaps:

```solidity
// OracleBase.sol L167
require(!blacklisted[pool], Blacklisted(pool));
```

The admin can blacklist a pool via `setBlacklist()` (ADMIN_ROLE gated). However, the permissionless `register()` function unconditionally clears the blacklist for any pool that pays the registration fee:

```solidity
// OracleBase.sol L201-L213
function register(bytes32 feedId, address pool, address factory) external payable {
    require(msg.value >= registrationFee, InsufficientFee(msg.value, registrationFee));
    require(pool != address(0));
    require(approvedFactories.contains(factory), FactoryNotApproved(factory));
    require(IPoolFactory(factory).isPool(pool), NotAPool(pool));

    if (blacklisted[pool]) {
        blacklisted[pool] = false;          // ← blacklist cleared by anyone
        emit BlacklistUpdated(pool, false);
    }

    registeredPool[feedId][pool] = true;
    emit PoolRegistered(feedId, pool, msg.sender, msg.value);
}
```

The `registrationFee` is initialized to 1 wei:

```solidity
// OracleBase.sol L53
registrationFee = 1 wei; // very cheap default; ADMIN tunes via setRegistrationFee
```

**Attack path:**
1. Admin calls `setBlacklist(pool, true)` to block a malicious or compromised pool from reading oracle prices.
2. The pool operator (or any third party) calls `register(feedId, pool, factory)` with 1 wei.
3. The `if (blacklisted[pool])` branch fires, sets `blacklisted[pool] = false`.
4. The pool can now call `price(feedId, pool)` again and execute swaps using oracle data.

The admin must race to raise `registrationFee` or remove the factory approval to prevent re-registration, but neither is atomic with the blacklist action.

---

### Impact Explanation

The oracle blacklist is the only on-chain mechanism to cut off a pool from price data. If a pool is blacklisted (e.g., due to detected manipulation, insolvency, or a compromised operator), it can immediately self-clear the blacklist for 1 wei and resume reading oracle prices. This allows the pool to continue executing swaps at oracle-derived prices, potentially draining counterparty funds or continuing harmful behavior that the admin intended to stop. The admin's enforcement capability is completely nullified.

---

### Likelihood Explanation

The bypass requires only a valid factory and pool address (both publicly known on-chain) and 1 wei. No privileged access, no special role, no complex setup. Any pool operator — or even an anonymous third party — can execute this in a single transaction immediately after the admin blacklists the pool.

---

### Recommendation

Remove the blacklist-clearing side-effect from `register()`. Blacklist management should be exclusively admin-controlled. If re-registration after blacklist removal is desired, require an explicit admin action first:

```solidity
function register(bytes32 feedId, address pool, address factory) external payable {
    require(msg.value >= registrationFee, InsufficientFee(msg.value, registrationFee));
    require(pool != address(0));
    require(!blacklisted[pool], Blacklisted(pool)); // ← reject blacklisted pools
    require(approvedFactories.contains(factory), FactoryNotApproved(factory));
    require(IPoolFactory(factory).isPool(pool), NotAPool(pool));

    registeredPool[feedId][pool] = true;
    emit PoolRegistered(feedId, pool, msg.sender, msg.value);
}
```

---

### Proof of Concept

```solidity
// 1. Admin blacklists the pool
oracle.setBlacklist(address(pool), true);
assert(oracle.blacklisted(address(pool)) == true);

// 2. Pool operator re-registers with 1 wei — blacklist cleared
oracle.register{value: 1 wei}(feedId, address(pool), address(factory));
assert(oracle.blacklisted(address(pool)) == false);  // bypass complete

// 3. Pool reads oracle price again — no revert
(uint256 mid, , , ) = oracle.price(feedId, address(pool));
// swap proceeds at oracle price
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L49-54)
```text
    constructor(address _owner, uint256 maxTimeDrift) {
        _grantRole(ADMIN_ROLE, _owner);
        _setRoleAdmin(ADMIN_ROLE, ADMIN_ROLE);
        MAX_TIME_DRIFT = maxTimeDrift;
        registrationFee = 1 wei; // very cheap default; ADMIN tunes via setRegistrationFee
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L160-172)
```text
    function price(bytes32 feedId, address pool)
        external
        feedExists(feedId)
        notBlacklisted
        returns (uint256 mid, uint256 spread, uint16 spread1, uint256 refTime)
    {
        require(pool != address(0) && IPool(pool).inSwap() == msg.sender, InvalidInSwap());
        require(!blacklisted[pool], Blacklisted(pool));
        require(registeredPool[feedId][pool], NotRegistered(feedId, pool));

        (mid, spread, spread1, refTime) = _readPrice(feedId);
        emit PriceRead(pool, feedId);
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L201-214)
```text
    function register(bytes32 feedId, address pool, address factory) external payable {
        require(msg.value >= registrationFee, InsufficientFee(msg.value, registrationFee));
        require(pool != address(0));
        require(approvedFactories.contains(factory), FactoryNotApproved(factory));
        require(IPoolFactory(factory).isPool(pool), NotAPool(pool));

        if (blacklisted[pool]) {
            blacklisted[pool] = false;
            emit BlacklistUpdated(pool, false);
        }

        registeredPool[feedId][pool] = true;
        emit PoolRegistered(feedId, pool, msg.sender, msg.value);
    }
```

**File:** smart-contracts-poc/contracts/oracles/providers/OracleBase.sol (L271-276)
```text
    function setBlacklist(address account, bool value) external onlyRole(ADMIN_ROLE) {
        require(account != address(0));
        if (blacklisted[account] == value) return;
        blacklisted[account] = value;
        emit BlacklistUpdated(account, value);
    }
```

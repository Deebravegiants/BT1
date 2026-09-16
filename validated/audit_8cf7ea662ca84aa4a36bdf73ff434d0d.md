### Title
`IntentGatewayV2` (Tron) constructor accepts a null `admin`, permanently bricking the contract — ([File: evm/tron/contracts/apps/IntentGatewayV2.sol])

### Summary
The Tron variant of `IntentGatewayV2` is constructed with an `admin` address that is never checked against `address(0)`, unlike its EVM counterpart. Since `_admin` is the sole gate for the one-shot `setParams` call that configures the gateway (`host`, `dispatcher`, fees, etc.), a zero `admin` makes the contract permanently unconfigurable — `host()` stays `address(0)` forever and the contract can never process any cross-chain order.

### Finding Description
`evm/tron/contracts/apps/IntentGatewayV2.sol` constructor simply stores whatever address is passed, with no validation: [1](#0-0) 

Compare this with the canonical EVM `IntentGatewayV2` implementation, which explicitly rejects `address(0)` for the equivalent `owner` parameter: [2](#0-1) 

In the Tron contract, `_admin` is the only account permitted to call `setParams`, which is the sole way to populate `_params` (including `host`, `dispatcher`, `priceOracle`, fee settings): [3](#0-2) 

`setParams` checks `if (msg.sender != _admin) revert Unauthorized();` and then permanently zeroes `_admin` after use, meaning it is designed to be called exactly once by the deployer-designated admin. If `_admin` is `address(0)` at construction, no ordinary transaction can ever satisfy `msg.sender == _admin` (an EOA cannot originate a transaction as the zero address), so `setParams` can never succeed. `_params.host` therefore remains `address(0)` forever, `host()` returns `address(0)`, and every ISMP dispatch/accept path guarded by `host()`/`_params` becomes unusable.

### Impact Explanation
This is a permanent freeze/denial-of-service condition on the deployed contract: an incorrectly-parameterized deployment (or a supply-chain/deployment-script mistake passing a zero admin) results in a gateway that can receive native tokens via its `receive()` function but can never be configured, and thus can never fulfill or refund any intent routed to it, and any funds sent to it are permanently stuck with no privileged recovery path (since `_admin` is also zero, no governance-style fallback exists). This matches "permanent freezing of funds" / "route unable to deliver messages" impact criteria.

### Likelihood Explanation
Likelihood is deployment-configuration-dependent rather than exploitable by an arbitrary unprivileged attacker post-deployment — the flaw is triggered only if the contract is constructed with a null `admin`. However, per the audit-analog bug class (a constructor accepting a null critical address with no sanity check, unlike its sibling implementation which already fixes this), this is a legitimate and low-cost defensive gap: there is no reason not to add the same check that the EVM `IntentGatewayV2` already has, and the asymmetry between the two implementations of the "same" contract is itself evidence of an overlooked fix.

### Recommendation
Add a zero-address check in the Tron `IntentGatewayV2` constructor mirroring the EVM implementation:
```solidity
constructor(address admin) EIP712("IntentGateway", "2") {
    if (admin == address(0)) revert InvalidInput();
    _admin = admin;
}
```

### Proof of Concept
1. Deploy `evm/tron/contracts/apps/IntentGatewayV2.sol` with `admin = address(0)`.
2. Attempt to call `setParams(p)` from any account — `msg.sender != _admin` is always true (no account can transact as `address(0)`), so the call always reverts with `Unauthorized`.
3. `_params.host` remains `address(0)` and `host()` returns `address(0)` indefinitely; the contract can never process `onAccept` cross-chain messages or dispatch orders that depend on valid `_params`.
4. Any native tokens sent to the contract via its `receive()` function are now permanently unrecoverable, since no privileged path exists to sweep them.

### Citations

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L257-259)
```text
    constructor(address admin) EIP712("IntentGateway", "2") {
        _admin = admin;
    }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L302-311)
```text
    /**
     * @notice Sets the parameters for the IntentGateway.
     * @param p The parameters to be set, encapsulated in a Params struct.
     */
    function setParams(Params memory p) public {
        if (msg.sender != _admin) revert Unauthorized();

        _admin = address(0);
        _params = p;
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L71-75)
```text
    constructor(address owner) EIP712("IntentGateway", "2") {
        if (owner == address(0)) revert InvalidInput();
        _owner = owner;
        _disableInitializers();
    }
```

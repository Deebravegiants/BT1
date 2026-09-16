### Title
Missing storage gap in the upgradeable abstract base `IntentsBase` risks corrupting escrow state on future upgrades - (File: evm/src/apps/intentsv2/IntentsBase.sol)

### Summary
`IntentsBase` is an `abstract contract` that declares all of `IntentGatewayV2`'s persistent storage (`_filled`, `_nonce`, `_params`, `_orders`, `_instances`, `_partialFills`, `_destinationProtocolFees`, `_paused`, `_relayer`) and is inherited by `IntrinsicIntents` and `ExtrinsicIntents`, which are both inherited by the concrete, upgradeable, ERC1967-proxied `IntentGatewayV2` contract. [1](#0-0)  Unlike `SimplexPaymaster.sol`, which reserves a `uint256[48] private __gap;` at the end of its storage layout to safely absorb future variables, [2](#0-1)  `IntentsBase` has no such gap after its final declared variable `_relayer`. [3](#0-2) 

### Finding Description
`IntentsBase` declares its storage in this order: `_filled` (slot 2, load-bearing for the cross-chain cancel proof via `FILLED_SLOT_BIG_ENDIAN_BYTES`), `_nonce`, `_params` (slots 4-8), `_orders` (slot 9), `_instances`, `_partialFills`, `_destinationProtocolFees`, `_paused`, and `_relayer` (packed into slot 13). [3](#0-2)  This layout is documented as extremely fragile — the project's own decision log notes that `Params` occupies slots 4-8 and `_orders` starts at slot 9, and that adding a field to `Params` would push every mapping behind it and corrupt escrow on the live proxy. [4](#0-3)  A dedicated foundry test also pins `_filled` to storage slot 2 specifically because a cross-chain proof depends on that exact slot. [5](#0-4) 

`IntentGatewayV2` is deployed behind an `ERC1967Proxy`, uses `Initializable`/`reinitializer`, and is upgraded via a Hyperbridge-governed `UpgradeContract`/`Execute` flow that calls `ERC1967Utils.upgradeToAndCall`. [6](#0-5)  The project's own changelog shows this is an actively evolving contract — a live-mainnet proxy has already been migrated once (`VERSION` bumped, `_relayer`/`_paused` added after the fact) via governance-controlled implementation swaps. [7](#0-6) 

Because `IntentsBase` is the abstract root of the inheritance diamond (`IntentsBase → IntrinsicIntents, ExtrinsicIntents → IntentGatewayV2`) [8](#0-7)  and has no reserved storage gap, any future implementation that needs to add a new state variable to `IntentsBase` (a very plausible need, given how much cross-chain escrow/governance logic already lives there) has only two unsafe options: (1) append the new variable after `_relayer`, which is safe only as long as no derived contract or sibling abstract contract in the diamond has *already* claimed the following slot for its own storage, or (2) insert it earlier, which — as the project's own decision doc warns — shifts every mapping behind it and corrupts live escrow data (`_orders`, `_filled`, `_partialFills`) read from now-wrong storage slots. Without an explicit `__gap`, developers have no forcing function preventing the second, catastrophic case, and no headroom guaranteed to be free of collisions from other branches of the diamond inheritance.

### Impact Explanation
If a future upgrade to `IntentsBase` (or any intermediate abstract contract in this diamond) adds a state variable without careful, error-prone slot accounting, it can silently reinterpret existing storage slots. Given that `_filled`, `_orders`, and `_partialFills` are the exact mappings that gate escrow release/redemption/refund of user and solver funds, a slot collision after such an upgrade could let already-filled orders be treated as unfilled (double-release of escrow) or valid escrow balances be read as zero/garbage (permanent freezing of funds), and would corrupt the `_filled`-slot-based cross-chain cancel proof (`FILLED_SLOT_BIG_ENDIAN_BYTES`) that the whole cross-chain redemption protocol depends on. This is a proxy-upgrade-time risk on a contract that has already been upgraded once on live mainnet deployments (`IntentGatewayV2Test.sol`'s `LIVE_GATEWAY` fork tests) and is designed for further governance-driven upgrades.

### Likelihood Explanation
This is not exploitable by an ordinary unprivileged transaction today — it requires a future contract upgrade. However, `IntentGatewayV2`'s upgrade path is a normal, expected part of this protocol's operation (governance regularly ships new implementations through `UpgradeContract`/`Execute`, as shown by the existing `migrate`/`VERSION` machinery and the live-proxy upgrade tests). Given the demonstrated pattern of iterative storage additions to `IntentsBase` (e.g., `_paused` and `_relayer` were both appended after the fact, as documented in the decision log), the likelihood of a slot-corrupting change being introduced in a subsequent upgrade is non-trivial specifically because there is no `__gap` reservation forcing safe append-only growth in the deepest abstract layer of the diamond.

### Recommendation
Add an explicit storage gap to `IntentsBase` (and any other abstract contract in the `IntentGatewayV2` inheritance diamond that declares its own storage, e.g. `ExtrinsicIntents`/`IntrinsicIntents` if they hold state), following the same pattern already used in `SimplexPaymaster.sol`:
```solidity
uint256[50] private __gap;
```
placed after the last currently-declared storage variable (`_relayer`). This reserves headroom so future variables can be safely appended without needing to reason about slot collisions across the diamond, consistent with the standard OpenZeppelin upgradeable-contract storage-gap convention already partially adopted elsewhere in this codebase.

### Proof of Concept
No transaction-level PoC applies since this is a storage-layout design defect that only manifests on a future code change, not an exploitable bug in the current bytecode. The risk is demonstrated structurally:
- `IntentsBase` declares 9 storage slots' worth of state ending at `_relayer` with no gap. [3](#0-2) 
- `SimplexPaymaster.sol`, a sibling upgradeable governance contract in the same codebase, already recognizes this risk class and mitigates it with `uint256[48] private __gap;`. [2](#0-1) 
- The project's own documentation independently confirms that inserting fields into this exact storage region ("`Params` occupies slots 4 to 8 and `_orders` starts at slot 9. Adding a field to the struct would push every mapping behind it and corrupt escrow on the live proxy.") is a known, previously-considered failure mode for this contract. [9](#0-8)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L46-52)
```text
 * @title IntentsBase
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @dev Abstract base contract for the IntentGateway. Contains all shared state,
 * constants, errors, events, and chain-agnostic utility functions.
 */
abstract contract IntentsBase is EIP712 {
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L122-173)
```text
    /**
     * @dev Maps order commitment hashes to the address that filled or refunded the order.
     * A non-zero value indicates the order has been finalized and cannot be filled again.
     */
    mapping(bytes32 => address) public _filled;

    /**
     * @dev Monotonically increasing counter used to assign unique nonces to orders.
     * Each call to `placeOrder` consumes and increments this value.
     */
    uint256 public _nonce;

    /**
     * @dev Gateway configuration parameters including host address, dispatcher,
     * fee settings, price oracle, and solver selection toggle.
     */
    Params internal _params;

    /**
     * @dev Maps (commitment, token address) to the escrowed amount for that token.
     * Decremented as tokens are released via fills or refunds.
     */
    mapping(bytes32 => mapping(address => uint256)) public _orders;

    /**
     * @dev Maps keccak256(stateMachineId) to the registered gateway address for
     * that chain. Used for authenticating cross-chain messages and routing dispatches.
     * Read through `instance(bytes)`; the auto-generated getter was dropped for EIP-170 room.
     */
    mapping(bytes32 => address) internal _instances;

    /**
     * @dev Maps (commitment, output token) to the cumulative amount already filled.
     * Used to track partial fill progress for same-chain orders.
     */
    mapping(bytes32 => mapping(bytes32 => uint256)) public _partialFills;

    /**
     * @dev Maps keccak256(stateMachineId) to a destination-specific protocol fee
     * override in basis points. If zero, the global `_params.protocolFeeBps` is used.
     */
    mapping(bytes32 => uint256) public _destinationProtocolFees;

    /// @dev Appended last to preserve existing storage slots.
    bool internal _paused;

    /**
     * @dev Once set, the only relayer whose deliveries `onAccept` and `onGetResponse` accept.
     * Read through `relayer()`; an auto-generated getter on top of that would not fit under
     * EIP-170.
     */
    address internal _relayer;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L211-212)
```text

    uint256[48] private __gap;
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-03-the-relayer-is-a-separate-storage-variable-not-a-params-field.md (L1-9)
```markdown
# 2026-09-03 — The relayer is a separate storage variable, not a `Params` field

Chosen: `address _relayer` appended after `_paused` in `IntentsBase`, set through its own
`setRelayer` call.

`Params` occupies slots 4 to 8 and `_orders` starts at slot 9. Adding a field to the struct would
push every mapping behind it and corrupt escrow on the live proxy. Reusing `UpdateParams` was
therefore never available, quite apart from it being a Hyperbridge-relayed message: the whole point
is to hold even if Hyperbridge's consensus is compromised, so the setter must not depend on it.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4124-4134)
```text
    function testFilledMappingStaysAtSlotTwo() public {
        (bytes32 filledCommitment,,,) = _seedUpgradeState();

        // _filled is `mapping(bytes32 => address)` declared at storage slot 2. The cross-chain
        // cancel proof (FILLED_SLOT_BIG_ENDIAN_BYTES) depends on this exact slot.
        bytes32 slot = keccak256(abi.encode(filledCommitment, uint256(2)));
        address filledFromSlot = address(uint160(uint256(vm.load(address(intentGateway), slot))));

        assertEq(filledFromSlot, filler, "_filled must occupy storage slot 2");
        assertEq(filledFromSlot, intentGateway._filled(filledCommitment), "slot-2 read matches getter");
    }
```

**File:** evm/src/apps/IntentGatewayV2.sol (L45-75)
```text
/**
 * @title IntentGatewayV2
 * @author Polytope Labs (hello@polytope.technology)
 *
 * @dev The IntentGateway allows for the creation and fulfillment of same-chain & cross-chain orders.
 * This is the concrete entry-point contract that composes all intent logic via inheritance:
 *
 *            EIP712
 *              |
 *          IntentsBase
 *           /       \
 *  IntrinsicIntents  ExtrinsicIntents
 *           \       /
 *        IntentGatewayV2
 */
contract IntentGatewayV2 is IntrinsicIntents, ExtrinsicIntents, ReentrancyGuardTransient, Initializable {
    using SafeERC20 for IERC20;

    /// @dev Privileged admin for future upgrade-gated actions (e.g. pausing). Immutable, so it must
    /// be identical across chains or the deterministic proxy address diverges. Does not gate
    /// `initialize`; atomic CREATE2 deployment already binds the init data to the canonical address.
    address public immutable _owner;

    /// @dev Sets the EIP-712 domain ("IntentGateway", "2"), records the admin, and locks this raw
    /// implementation against direct initialization.
    /// @param owner The privileged admin address.
    constructor(address owner) EIP712("IntentGateway", "2") {
        if (owner == address(0)) revert InvalidInput();
        _owner = owner;
        _disableInitializers();
    }
```

**File:** sdk/packages/core/docs/ai/changelog/2026-09-05-gateway-initialize-refused-on-any-proxy-already-at-a-version.md (L1-12)
```markdown
# 2026-09-05 — Gateway `initialize` refused on any proxy already at a version

`initialize` carries an `onlyFresh` modifier that reverts with `InvalidInitialization` unless the
`Initializable` version is 0. Without it, an upgrade that installed this implementation on a
version-1 proxy without running `migrate` would leave `initialize`, which has no caller
restriction, open to anyone until governance caught up. Now the host-only `migrate` is the only
way up for such a proxy. `testInitializeRefusedOnLegacyProxy` plays it. The interface NatSpec for
`migrate` says so.

Files: `contracts/apps/IntentGatewayV2.sol`, `docs/ai/ChangeLog.md`, `docs/ai/Decisions.md`,
`docs/ai/Flow.md`. Outside the package: `evm/src/apps/IntentGatewayV2.sol`,
`evm/tests/foundry/IntentGatewayV2Test.sol`.
```

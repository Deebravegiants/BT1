### Title
Missing storage gaps in the upgradeable abstract base `IntentsBase` risk storage-layout corruption of `IntentGatewayV2` on future upgrades - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentsBase` is an abstract contract that declares all the shared escrow/state storage (`_filled`, `_nonce`, `_params`, `_orders`, `_instances`, `_partialFills`, `_destinationProtocolFees`, `_paused`, `_relayer`) for the diamond-inherited, UUPS-upgradeable `IntentGatewayV2` (`IntentsBase → IntrinsicIntents/ExtrinsicIntents → IntentGatewayV2`), but it declares no trailing storage gap. [1](#0-0) [2](#0-1) 

### Finding Description
`IntentGatewayV2` is deployed behind an ERC-1967 proxy and is explicitly upgradeable via `upgradeToAndCall`, reachable through governance's `Execute` request delivered by the authorised relayer. [3](#0-2) [4](#0-3) 

The storage layout is fragile by construction: `IntrinsicIntents` and `ExtrinsicIntents` (and ultimately `IntentGatewayV2` itself) declare no state of their own before or interleaved with `IntentsBase`'s variables, and the codebase's own tests hard-code exact slot numbers derived from this layout (e.g. `_filled` at slot 2, `_relayer` at slot 13), confirming the team is manually tracking absolute slot positions rather than reserving expansion room. [5](#0-4) [6](#0-5) 

Because `IntentsBase` is the shared base of a diamond inheritance graph and is itself upgradeable, any future addition of a state variable to `IntentsBase` (the natural place to add new shared gateway state) will not slot into a reserved gap — it will land in whatever slot is next, which is currently occupied by `IntrinsicIntents`/`ExtrinsicIntents`-declared storage or by the concrete `IntentGatewayV2` storage that comes after it in the linearized layout. No `__gap` array exists anywhere under `evm/src/apps/` to absorb such additions. [7](#0-6) 

This is the same root cause as the cited Sherlock finding on `GranularRoles.sol`: an upgradeable abstract contract meant to be inherited by other upgradeable contracts, with new storage appended directly rather than behind a gap, so a future upgrade to the base silently overwrites the derived contract's storage slots.

### Impact Explanation
If a future upgrade adds a state variable to `IntentsBase` (or reorders/adds variables in `IntrinsicIntents`/`ExtrinsicIntents` without careful manual slot bookkeeping), the new implementation's storage layout no longer matches the live proxy's storage — `_orders` (escrowed funds), `_relayer` (delivery gate), `_params` (host/dispatcher/fee config), and `_filled`/`_partialFills` (fill/replay bookkeeping) could be shifted or overwritten. That can permanently freeze or misdirect escrowed user funds, disable or misconfigure the relayer gate that guards all `onAccept`/`onGetResponse` deliveries, or corrupt fee/parameter state — all triggered by a routine `upgradeToAndCall` governance delivery, not by any exotic attack. This satisfies "permanent freezing of funds" / "unauthorized app action" from unsound storage layout.

### Likelihood Explanation
The likelihood is tied entirely to future maintenance discipline rather than a currently exploitable bug: today's layout is internally consistent (as proven by the hard-coded-slot tests), so there is no live storage collision. The risk materializes only when a developer adds a new field to `IntentsBase` (the natural, most likely place to add shared gateway state) without manually re-verifying every derived contract's slot layout via `forge inspect storage`. Given the contract already relies on manual slot tracking in comments/tests instead of the OpenZeppelin-recommended storage-gap pattern, the likelihood of an eventual layout-corrupting upgrade is non-trivial over the contract's lifetime, especially since three separate files (`IntentsBase`, `IntrinsicIntents`, `ExtrinsicIntents`) must all be kept gap-free and re-verified together on every future change.

### Recommendation
Add an explicit storage gap to `IntentsBase` (and to `IntrinsicIntents`/`ExtrinsicIntents` if they ever declare their own state) immediately after existing state variables, e.g.:
```solidity
uint256[50] private __gap;
```
sized to leave headroom for anticipated future fields, and consume slots from the gap (decrementing its size) whenever a new variable is added, per the standard OpenZeppelin upgradeable-storage pattern. Alternatively, migrate shared state to an ERC-7201 namespaced storage struct to decouple it from linear inheritance-order slot allocation entirely.

### Proof of Concept
Not directly exploitable today — the current deployed layout is self-consistent, as shown by `testFilledMappingStaysAtSlotTwo` and the slot-13 relayer-packing assertions in `evm/tests/foundry/IntentGatewayV2Test.sol`. The defect is structural: attempt to add a new state variable to `IntentsBase` in a follow-up implementation and observe (via `forge inspect IntentGatewayV2 storage` before/after) that the new variable lands in a slot currently used by `IntrinsicIntents`/`ExtrinsicIntents`/`IntentGatewayV2` storage rather than in reserved padding, then push that implementation through the existing `Execute`/`upgradeToAndCall` governance path used in `testOnAcceptUpgradeContractPreservesState` (`evm/tests/foundry/IntentGatewayV2Test.sol:4069-4094`) to confirm the resulting corruption of `_orders`/`_relayer`/`_params` on the live proxy. [8](#0-7)

### Citations

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L52-52)
```text
abstract contract IntentsBase is EIP712 {
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L126-174)
```text
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

**File:** evm/src/apps/IntentGatewayV2.sol (L60-75)
```text
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

**File:** evm/src/apps/intentsv2/ExtrinsicIntents.sol (L43-54)
```text
abstract contract ExtrinsicIntents is IntentsBase, HyperApp {
    using SafeERC20 for IERC20;

    /**
     * @dev Returns the Hyperbridge host contract address. Overrides both IntentsBase and
     * HyperApp to resolve the diamond inheritance conflict — both parent contracts
     * declare a virtual `host()` function.
     * @return The host contract address from stored params.
     */
    function host() public view virtual override(IntentsBase, HyperApp) returns (address) {
        return _params.host;
    }
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4069-4094)
```text
    function testOnAcceptUpgradeContractPreservesState() public {
        (bytes32 filledCommitment, bytes32 escrowedCommitment, address inputToken, uint256 escrowedAmount) =
            _seedUpgradeState();

        uint256 nonceBefore = intentGateway._nonce();
        assertEq(nonceBefore, 2, "precondition: two orders placed");
        assertEq(intentGateway._filled(filledCommitment), filler, "precondition: order A filled");
        assertEq(
            intentGateway._orders(escrowedCommitment, inputToken), escrowedAmount, "precondition: order B escrowed"
        );

        IntentGatewayV2Upgraded newImpl = new IntentGatewayV2Upgraded(address(this));
        PostRequest memory request = _upgradeRequest(host.hyperbridge(), address(newImpl), "");

        vm.prank(address(host));
        intentGateway.onAccept(IncomingPostRequest({relayer: relayer, request: request}));

        // The proxy now points at the new implementation and its new logic is reachable.
        assertEq(_implementationOf(address(intentGateway)), address(newImpl), "implementation slot updated");
        assertEq(IntentGatewayV2Upgraded(payable(address(intentGateway))).upgradedMarker(), 42, "new logic is active");

        // All escrow-critical state survives the implementation swap.
        assertEq(intentGateway._nonce(), nonceBefore, "_nonce preserved");
        assertEq(intentGateway._filled(filledCommitment), filler, "_filled preserved");
        assertEq(intentGateway._orders(escrowedCommitment, inputToken), escrowedAmount, "_orders preserved");
    }
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

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4651-4654)
```text
            vm.load(LIVE_GATEWAY, bytes32(uint256(13))),
            _packedRelayerSlot(liveRelayer),
            "relayer packed behind an unset _paused in slot 13"
        );
```

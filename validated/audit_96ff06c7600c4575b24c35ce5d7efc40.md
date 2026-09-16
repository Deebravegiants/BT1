### Title
Front-runnable `initialize()` on `HyperFungibleTokenUpgradeable` / `WrappedHyperFungibleTokenUpgradeable` lets an attacker seize permanent ownership of a bridge-app token deployment - (File: `sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol`)

### Summary
`HyperFungibleTokenUpgradeable.initialize()` and `WrappedHyperFungibleTokenUpgradeable.initialize()` are `public` functions gated only by OpenZeppelin's `initializer` modifier (one-shot), with no restriction on `msg.sender`. Unlike `IntentGatewayV2` and `SimplexPaymaster` in the same codebase — which have documented decisions and tests specifically defending against this exact class of bug — these two upgradeable token apps carry no such protection and no atomic-deployment guarantee.

### Finding Description
Both contracts follow the standard OZ upgradeable pattern: the constructor only calls `_disableInitializers()` on the raw implementation [1](#0-0) , and `initialize` sets the ERC20 name/symbol and, critically, the `Ownable` owner: [2](#0-1) 

`WrappedHyperFungibleTokenUpgradeable.initialize` is identical in shape, setting only the owner: [3](#0-2) 

If a deployer deploys the proxy for either contract and calls `initialize` in a separate transaction (rather than passing init calldata atomically into the proxy constructor), any unprivileged address observing the pending proxy-deployment transaction can front-run it and call `initialize(name, symbol, attacker)` (or `initialize(attacker)`) first. Because `initializer` only prevents re-initialization, not caller identity, the attacker becomes the permanent `owner` of that token/bridge-app instance.

The codebase explicitly documents this exact bug class and the fix needed elsewhere: `IntentGatewayV2.initialize` deliberately has "no caller restriction, because a bare proxy is initialized atomically in its constructor" [4](#0-3) , and its production deploy path and test (`testAtomicInitialization`) enforce that `initialize` is only ever reached through the `ERC1967Proxy` constructor's init data, never as a free-standing call [5](#0-4) . `SimplexPaymaster` similarly documents this risk in its `onlyFresh`/`reinitializer` comments [6](#0-5) .

`HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleTokenUpgradeable` have no equivalent design note, no atomic-deployment test, and no caller gate at all on `initialize`. They are SDK library contracts intended to be deployed by third-party integrators building their own cross-chain token bridge apps on Hyperbridge — exactly the class of unprivileged deployment path in scope. Ownership grants `configure()` (sets the ISMP host and dispatcher, `onlyOwner`), `addChain`/`removeChain` (registers/removes trusted cross-chain peers, `onlyOwner`), and `pause`/`unpause` — meaning a hijacked deployment can be pointed at attacker-controlled peers or a malicious dispatcher, enabling forged/unauthorized minting via a spoofed `onAccept` path once `configure`/`addChain` are set by the new "owner": [7](#0-6) .

### Impact Explanation
An attacker who front-runs `initialize()` gains permanent, un-recoverable ownership of the deployed token/bridge-app instance (owner cannot be rotated by the legitimate deployer — there is no admin-recovery path). The attacker can then:
- Configure the ISMP host/dispatcher to values that let them mint tokens arbitrarily via a forged `onAccept` path (add a "supported chain" mapped to an address they control, then relay a fabricated cross-chain message accepted as legitimate).
- Or simply hold the contract hostage / deny legitimate configuration, permanently freezing the token app.

This matches "unauthorized app action" and "permanent freezing/unbacked mint" categories in scope.

### Likelihood Explanation
Exploitability depends entirely on the deployment procedure used by integrators. If proxies are always deployed with init calldata bundled atomically into the proxy constructor (as `IntentGatewayV2`'s tested production path does), the window does not exist. However, nothing in these two contracts enforces or documents that requirement, unlike `IntentGatewayV2`. Any integrator following the generic OZ upgradeable pattern of "deploy proxy, then call `initialize` separately" is directly exposed to public-mempool front-running on any chain without private mempools/relays.

### Recommendation
Mirror the mitigation already applied to `IntentGatewayV2`/`SimplexPaymaster` in this codebase:
1. Document and enforce atomic initialization — require deployers to pass `initialize` calldata into the proxy's constructor (`ERC1967Proxy(impl, initData)`), never as a separate call.
2. Add a deployment helper/script and a test (analogous to `testAtomicInitialization`) asserting the pattern, and/or add an explicit deployer-restriction check (e.g., compare `msg.sender` to a value committed to at proxy-construction time, or use a factory contract that atomically deploys + initializes in one transaction) so a bare `initialize()` call from an arbitrary EOA cannot succeed.

### Proof of Concept
1. Deployer calls `factory.deployProxy(HyperFungibleTokenUpgradeableImpl)` (or manually deploys an `ERC1967Proxy`/`TransparentUpgradeableProxy` with empty init data) intending to call `initialize("MyToken","MTK", deployer)` in a follow-up transaction.
2. Attacker observes the pending proxy-deployment transaction in the mempool, computes/derives the proxy address, and submits `initialize("MyToken","MTK", attacker)` with higher gas, landing before the deployer's own `initialize` call.
3. `initializer` modifier allows this because `_initialized` is false; the call succeeds and `Ownable` owner is set to `attacker`.
4. Deployer's later `initialize` call reverts (`InvalidInitialization`), and the deployer has no path to reclaim the contract — `attacker` now controls `configure`, `addChain`, `removeChain`, `pause`/`unpause` on the deployed token/bridge instance permanently.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L153-156)
```text
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L158-166)
```text
    /**
     * @notice Initializes the token with a name, symbol, and owner
     * @param name The name of the token
     * @param symbol The symbol of the token
     * @param initialOwner The address that will own this contract
     */
    function initialize(string memory name, string memory symbol, address initialOwner) public virtual initializer {
        __HyperFungibleToken_init(name, symbol, initialOwner);
    }
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L210-230)
```text
    /**
     * @notice Configures the host and dispatcher addresses
     * @dev Only callable by the contract owner
     * @param options The configuration parameters containing host and dispatcher addresses
     */
    function configure(ConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
    }

    /**
     * @notice Registers a supported chain and its corresponding token contract address
     * @dev Only callable by the contract owner. The address is the token contract on that chain.
     * @param chainId The chain identifier (e.g., StateMachine.evm(1))
     * @param moduleId The module ID of the peer on the specified chain (8 bytes for pallet, 20 bytes for EVM contract)
     */
    function addChain(bytes calldata chainId, bytes calldata moduleId) external onlyOwner {
        _supportedChains[chainId] = moduleId;
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L136-142)
```text
    /**
     * @notice Initializes the contract with the given owner
     * @param initialOwner The address that will own this contract
     */
    function initialize(address initialOwner) public virtual initializer {
        __WrappedHyperFungibleToken_init(initialOwner);
    }
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-05-initialize-only-on-a-bare-proxy-rather-than-a-version-check-in.md (L6-9)
```markdown
The hole both options close: `initialize` has no caller restriction, because a bare proxy is
initialized atomically in its constructor. An `UpgradeContract` that installs this implementation
on a version-1 proxy without `migrate` calldata would leave the proxy below `VERSION` with
`initialize` callable by anyone, who could then set the params and the relayer.
```

**File:** evm/tests/foundry/IntentGatewayV2Test.sol (L4096-4122)
```text
    /// @dev Production deploy path: the proxy initializes atomically via its init data, so the
    /// `initialize` call arrives through the proxy constructor (not from `_owner`). Must succeed.
    function testAtomicInitialization() public {
        IntentGatewayV2 implementation = new IntentGatewayV2(address(this));
        Params memory intentParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: 10000,
            protocolFeeBps: 0,
            priceOracle: address(0)
        });
        bytes[] memory peers = new bytes[](1);
        peers[0] = bytes("SOURCE_CHAIN");

        bytes memory initData = abi.encodeCall(IntentGatewayV2.initialize, (intentParams, peers, relayer));
        ERC1967Proxy proxy = new ERC1967Proxy(address(implementation), initData);
        IntentGatewayV2 gateway = IntentGatewayV2(payable(address(proxy)));

        assertEq(gateway.params().host, address(host), "params set via atomic init");
        assertEq(gateway.instance(bytes("SOURCE_CHAIN")), address(gateway), "peer bound to address(this)");
        assertEq(gateway.relayer(), relayer, "relayer armed from the init data");
        assertEq(gateway.version(), 2, "at VERSION from the init data");

        vm.expectRevert();
        gateway.initialize(intentParams, peers, address(0));
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L250-256)
```text
    /// @dev `initialize` is for a bare proxy only. A proxy that an upgrade left below `VERSION` is
    ///      taken there by the host-only `migrate`; without this, anyone could `initialize` it
    ///      with their own host.
    modifier onlyFresh() {
        if (_getInitializedVersion() != 0) revert InvalidInitialization();
        _;
    }
```

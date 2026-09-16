### Title
Uninitialized-proxy front-running on `HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleTokenUpgradeable` allows attacker takeover of a deterministic bridge deployment - (File: sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol, sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol)

### Summary
The Optimism/Wintermute incident lost 20M OP because a deterministic multisig address existed on-chain before its "arming" step (owner/threshold setup) executed, letting an attacker complete that arming step first and seize control of the address. Hyperbridge has the same structural bug class in its upgradeable HyperFungibleToken (HFT) apps: the proxy's address is deterministic (documented as deployed via CREATE2 with a shared salt for cross-chain consistency) but `initialize()`, which sets the owner and therefore who can call `configure()`/`addChain()`, is a plain OpenZeppelin `initializer` with no caller restriction and no atomicity guarantee tying it to the deployment transaction.

### Finding Description
`WrappedHyperFungibleTokenUpgradeable` (and identically-shaped `HyperFungibleTokenUpgradeable`) disable the implementation's initializers in the constructor but leave `initialize(address initialOwner)` open to anyone as long as the proxy has not yet been initialized: [1](#0-0) 

Unlike `IntentGatewayV2`, whose team explicitly documented and hardened this exact hazard, this contract's `initialize` has no `onlyFresh`-style caller-independent check beyond the standard `initializer` modifier, and the deploy flow documented for HFT contracts is "deploy first, `configure()`/`addChain()` afterward" rather than atomic constructor-bound init data: [2](#0-1) 

For the non-upgradeable `HyperFungibleToken`, this is safe because `initialOwner` is a constructor argument baked into the deployment transaction itself — ownership is atomic with deployment. For the Upgradeable variant behind a proxy, if the proxy is deployed with empty init data (as production `IntentGatewayV2` scripts show is a real pattern for bare proxies) and `initialize()` is called in a later, separate transaction, any observer of the mempool or of the known deterministic proxy address can call `initialize(attacker)` first and become the `Ownable` owner, gaining permanent control of `configure()` and `addChain()` — the same mechanism (arming a deterministic, still-unclaimed address before its intended controller does) that let the Optimism attacker seize the Wintermute multisig.

The project's own engineering notes confirm this exact bug class was previously found and had to be explicitly fixed for `IntentGatewayV2`: [3](#0-2) 
but no equivalent hardening (`onlyFresh`/atomic init-data binding) is present in `HyperFungibleTokenUpgradeable` or `WrappedHyperFungibleTokenUpgradeable`.

### Impact Explanation
If a `WrappedHyperFungibleTokenUpgradeable`/`HyperFungibleTokenUpgradeable` proxy is deployed non-atomically (proxy created, then `initialize` called separately — the same two-step flow the non-upgradeable HFT docs describe and that `IntentGatewayV2`'s own bare-proxy test fixtures use), an attacker who front-runs `initialize()` becomes the `Ownable` owner of the token/bridge contract. They can then call `addChain()` to register themselves as the trusted peer on every chain, causing legitimate `onAccept` deliveries from real peers to be rejected (permanent freezing/denial of message delivery) or, worse, register a malicious peer address that lets the attacker mint arbitrary tokens by forging POST requests routed through that channel — unbacked mint and outright fund theft, the same class of loss as the Optimism incident.

### Likelihood Explanation
This requires only a single front-run transaction against a known, deterministic (CREATE2) proxy address before the legitimate deployer's `initialize` call lands — exactly the situation SlowMist's report shows a real, sophisticated adversary is already watching for. It requires no special privilege, only mempool visibility or public knowledge of the pending deployment address, which the project's own multi-chain deployment scripts publish in advance for peer registration purposes.

### Recommendation
Apply the same fix already used for `IntentGatewayV2`: bind `initialize()` to the proxy's constructor init data so deployment and initialization are atomic in one transaction (as done via `ERC1967Proxy{salt}(address(implementation), initData)`), and/or add a caller-independent guard (`onlyFresh`/deployer-scoped check) so a stray, un-initialized proxy cannot be claimed by anyone other than its intended deployer.

### Proof of Concept
1. Deployer computes CREATE2 address of a `WrappedHyperFungibleTokenUpgradeable` ERC1967Proxy with empty init data and broadcasts the deployment transaction (as demonstrated by the analogous bare-proxy pattern used in `IntentGatewayV2`'s own tests: `evm/tests/foundry/IntentGatewayV2Test.sol:110-114`).
2. Attacker observes the deployment transaction in the mempool (or simply knows the deterministic address in advance, since it is published for cross-chain peer registration), and submits `initialize(attacker)` with higher gas, landing before the deployer's own follow-up initialize call.
3. Attacker is now `owner()`; they call `addChain()`/`configure()` to reroute or forge trusted peer bindings, then trigger `onAccept` deliveries from a spoofed "peer" to mint tokens to themselves, or block legitimate delivery entirely by rejecting the true peer's messages via `UnauthorizedSource`. [4](#0-3)

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L131-140)
```text
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the contract with the given owner
     * @param initialOwner The address that will own this contract
     */
    function initialize(address initialOwner) public virtual initializer {
```

**File:** docs/content/developers/evm/hyper-fungible-token/hyper-fungible-token.mdx (L14-41)
```text
<Steps>
<Step>
### Deploy with CREATE2

Use CREATE2 for deterministic addresses across all chains.

```solidity lineNumbers
import {HyperFungibleToken} from "@hyperbridge/core/apps/HyperFungibleToken.sol";
import {IHyperFungibleToken} from "@hyperbridge/core/interfaces/IHyperFungibleToken.sol";

bytes32 salt = keccak256("my-token-v1");
HyperFungibleToken token = new HyperFungibleToken{salt: salt}("Wrapped USDC", "wUSDC", msg.sender);
```
</Step>
<Step>
### Configure

```solidity lineNumbers
IHyperFungibleToken(address(token)).configure(
    IHyperFungibleToken.ConfigOptions({
        host: ISMP_HOST_ADDRESS,
        dispatcher: CALL_DISPATCHER_ADDRESS
    })
);
```

Find the `IsmpHost` address for your chain on the [contract addresses](/developers/evm/contract-addresses/mainnet) page.
</Step>
```

**File:** sdk/packages/core/docs/ai/decisions/2026-09-05-initialize-only-on-a-bare-proxy-rather-than-a-version-check-in.md (L1-9)
```markdown
# 2026-09-05 — `initialize` only on a bare proxy, rather than a version check in the upgrade path

Chosen: `initialize` is refused unless the proxy is at version 0. `migrate` is the only entry to
`VERSION` for a proxy that already has one, and it is host-only.

The hole both options close: `initialize` has no caller restriction, because a bare proxy is
initialized atomically in its constructor. An `UpgradeContract` that installs this implementation
on a version-1 proxy without `migrate` calldata would leave the proxy below `VERSION` with
`initialize` callable by anyone, who could then set the params and the relayer.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L103-125)
```text
    /// @notice Thrown when the provided bytes are too short to extract an address
    error InvalidAddress(uint256 length);

    /// @notice Thrown when attempting to send to or receive from an unconfigured chain
    error UnsupportedChain();

    /**
     * @notice Thrown when the source address of an incoming message does not match the
     * expected contract address for that chain
     */
    error UnauthorizedSource();

    /// @notice Address of the ISMP host contract on this chain
    address internal _host;

    /// @notice Address of the CallDispatcher contract for executing destination calldata
    address internal _dispatcher;

    /**
     * @notice Maps chain identifiers to the module ID of the peer on that chain.
     * An empty value means the chain is not supported.
     */
    mapping(bytes => bytes) internal _supportedChains;
```

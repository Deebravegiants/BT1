### Title
Missing `__gap` storage reservation in `HyperFungibleTokenUpgradeable` / `WrappedHyperFungibleTokenUpgradeable` risks storage-collision on future upgrades - (File: sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol, sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol)

### Summary
`HyperFungibleTokenUpgradeable` and `WrappedHyperFungibleTokenUpgradeable` are both designed as UUPS/proxy-upgradeable ISMP token-bridge applications — each is `Initializable`, disables its own initializers in the constructor for use as an implementation behind a proxy, and inherits multiple OpenZeppelin `*Upgradeable` base contracts. Neither contract reserves a `__gap` storage array at the end of its own declared storage variables, unlike the sibling upgradeable contract `SimplexPaymaster`, which explicitly reserves `uint256[48] private __gap;` after its own state.

### Finding Description
Both contracts declare implementation-owned storage variables directly after the imported OZ upgradeable bases, with no reserved padding slots at the end: [1](#0-0) [1](#0-0) 

```
address internal _host;
address internal _dispatcher;
mapping(bytes => bytes) internal _supportedChains;
...
constructor() {
    _disableInitializers();
}
```

Similarly for the wrapped variant: [2](#0-1) 

Both contracts explicitly document themselves as "Upgradeable" applications intended to sit behind a proxy (`@custom:oz-upgrades-unsafe-allow constructor`, `_disableInitializers()`), and `WrappedHyperFungibleTokenUpgradeable` even reuses the naming/structure of `HyperFungibleTokenUpgradeable`, implying a shared lineage/future extension pattern. By contrast, the codebase's own established pattern for this exact class of bug — an upgradeable contract reachable from cross-chain governance execution — is to reserve a fixed-size `__gap` array, as seen in `SimplexPaymaster`: [3](#0-2) 

Without an equivalent `__gap` in `HyperFungibleTokenUpgradeable` / `WrappedHyperFungibleTokenUpgradeable`, any future version that adds new state variables to these base contracts (e.g., an added fee parameter, allow-list, or additional peer-chain mapping) will silently shift the storage slots of all variables declared after the insertion point across every existing proxy deployment. Because these contracts mix ERC20/ERC165/Ownable/Pausable upgradeable bases with custom-declared mappings (`_supportedChains`) that determine chain routing and token balances, a slot-shift on upgrade can point live `_host`, `_dispatcher`, `_supportedChains`, `_underlying`, or `_isWeth` values at the wrong storage slots, corrupting the app's routing/authorization state or the underlying-token bookkeeping used for mint/burn accounting on live proxies.

### Impact Explanation
These contracts are self-custody, per-deployment ISMP bridge applications that mint/burn tokens (or lock/unlock underlying ERC-20/native assets) directly in response to relayed cross-chain messages via `HyperApp`'s `onAccept`. If a future upgrade to the base contract inadvertently shifts storage layout because no `__gap` reserve exists, a live proxy's `_host` (the only address authorized to deliver ISMP messages) or `_supportedChains` (chain authorization mapping) could be corrupted post-upgrade, potentially allowing unauthorized mint/unlock of tokens or breaking chain-authorization checks — a concrete path to unbacked mint or theft of escrowed/underlying funds. This mirrors the Medium-severity classification of the original `AvailBridge` report: the vulnerability is latent (triggered only by a future storage-layout change), but the consequence when triggered is a fund-safety issue in a live token bridge.

### Likelihood Explanation
Likelihood is inherent to the maintenance lifecycle of an upgradeable contract rather than to a single malicious actor: any developer who later adds a state variable to `HyperFungibleTokenUpgradeable` or `WrappedHyperFungibleTokenUpgradeable` (or to a base OZ upgradeable dependency bump that changes its own gap usage) without manually auditing every derived proxy's slot layout will trigger the collision on the next upgrade. Given the project already treats this exact risk seriously elsewhere (`SimplexPaymaster`'s `__gap`), the omission here is inconsistent internal practice, and the token-bridge contracts are exactly the kind of contract likely to receive incremental feature additions (new peer chains, new calldata modes) over time.

### Recommendation
Append a fixed-size `uint256[N] private __gap;` array as the last declared storage variable in both `HyperFungibleTokenUpgradeable` and `WrappedHyperFungibleTokenUpgradeable` (sized so each contract's own storage plus gap sums to a fixed slot budget, e.g. 50), consistent with the pattern already used in `SimplexPaymaster`. Reduce the gap size by exactly the number of slots consumed whenever new storage variables are added in a future version, to preserve the fixed total and protect every already-deployed proxy from layout collisions.

### Proof of Concept
Conceptual PoC (storage-layout diff, not a runtime exploit):
1. Deploy `WrappedHyperFungibleTokenUpgradeable` behind a proxy; `_host`, `_dispatcher`, `_underlying`, `_isWeth`, `_supportedChains` occupy slots immediately following the inherited OZ upgradeable bases' storage.
2. Ship a v2 implementation that adds one new state variable (e.g. `address internal _feeRecipient;`) directly after `_isWeth` and before `_supportedChains`, without any `__gap` buffer to consume.
3. Upon `upgradeToAndCall` to v2, `_supportedChains`'s storage slot shifts by one slot; reads of `_supportedChains[chainId]` now resolve to whatever was previously stored at the *next* slot (uninitialized/garbage in a fresh deployment, or another live variable's data on an existing proxy), corrupting authorized chain routing and potentially allowing messages from/to unauthorized `dest`/`from` bytes to pass the chain-authorization check used in `Sent`/`Received` mint-burn logic.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L115-156)
```text
    /// @notice Address of the ISMP host contract on this chain
    address internal _host;

    /// @notice Address of the CallDispatcher contract for executing destination calldata
    address internal _dispatcher;

    /**
     * @notice Maps chain identifiers to the module ID of the peer on that chain.
     * An empty value means the chain is not supported.
     */
    mapping(bytes => bytes) internal _supportedChains;

    /**
     * @notice Emitted when tokens are burned and a cross-chain transfer is dispatched
     * @param from The sender on the source chain
     * @param to The recipient on the destination chain
     * @param dest The destination chain identifier
     * @param amount The amount of tokens sent
     * @param commitment The ISMP request commitment hash for tracking
     */
    event Sent(address from, bytes to, string dest, uint256 amount, bytes32 commitment);

    /**
     * @notice Emitted when tokens are minted from an incoming cross-chain transfer
     * @param from The original sender on the source chain
     * @param to The recipient on this chain
     * @param source The source chain identifier
     * @param amount The amount of tokens minted
     */
    event Received(bytes from, address to, string source, uint256 amount);

    /**
     * @notice Emitted when tokens are refunded after a cross-chain transfer timeout
     * @param to The original sender being refunded
     * @param amount The amount of tokens refunded
     */
    event Refunded(address to, uint256 amount);

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L48-95)
```text
contract WrappedHyperFungibleTokenUpgradeable is
    Initializable,
    ERC165Upgradeable,
    HyperApp,
    OwnableUpgradeable,
    PausableUpgradeable
{
    using SafeERC20 for IERC20;

    /**
     * @title WrappedConfigOptions
     * @notice Configuration parameters for WrappedHyperFungibleTokenUpgradeable
     */
    struct WrappedConfigOptions {
        /// @notice Address of the ISMP host contract on this chain
        address host;
        /// @notice Address of the CallDispatcher contract for executing calldata on receive
        address dispatcher;
        /// @notice Address of the underlying ERC20 token to wrap
        address underlying;
        /// @notice Whether the underlying token is WETH (enables native ETH refunds on timeout)
        bool isWeth;
    }

    /// @notice Thrown when the provided bytes are too short to extract an address
    error InvalidAddress(uint256 length);

    /// @notice Thrown when a native ETH transfer fails during timeout refund
    error TransferFailed();

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

    /// @notice The underlying ERC20 token being wrapped for cross-chain transfers
    address internal _underlying;

```

**File:** evm/src/utils/SimplexPaymaster.sol (L209-216)
```text
    /// @dev The only relayer whose `onAccept` deliveries are accepted; zero means every relayer.
    address private _relayer;

    uint256[48] private __gap;

    /// @dev The `Initializable` version this implementation lands a proxy on, through `initialize`
    ///      or `migrate`. Bumped by the next implementation that needs a migration.
    uint64 private constant VERSION = 2;
```

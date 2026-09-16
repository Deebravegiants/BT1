## Title
Base bridge token contracts use `initializer` instead of `onlyInitializing` on virtual `initialize`, blocking derived-contract initialization - (File: `sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol`, `sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol`)

### Summary
`HyperFungibleTokenUpgradeable` and `WrappedHyperFungibleTokenUpgradeable` are upgradeable base contracts explicitly designed to be extended (`public virtual initializer` on the outer function, plus a dedicated internal `__..._init` helper correctly guarded with `onlyInitializing` for "derived contracts"). However, the top-level `initialize` function itself is guarded with OpenZeppelin's `initializer` modifier rather than `onlyInitializing`, exactly the pattern flagged in the referenced Sherlock report for `MasterAMO`.

### Finding Description
Both token bridge base contracts declare their public `initialize` entrypoint as `virtual` and are clearly intended to be inherited by concrete deployments (each token deployment "is its own bridge application"): [1](#0-0) [2](#0-1) 

The NatSpec on the internal helper explicitly states it exists to "initialize the inherited upgradeable modules for **derived contracts**," confirming the inheritance intent. The internal helpers (`__HyperFungibleToken_init`, `__WrappedHyperFungibleToken_init`) are correctly marked `onlyInitializing`, but the outer, callable `initialize` function that a derived contract's own `initialize` would need to invoke (via `super.initialize(...)`) is marked with `initializer`, not `onlyInitializing`.

Per OpenZeppelin's `Initializable`, `initializer` can be invoked **at most once in the whole call tree** and reverts with `InvalidInitialization` if it detects it is being called while already inside an initialization context created by another `initializer`-guarded function. If a project derives a new token contract from `HyperFungibleTokenUpgradeable` (or the wrapped variant) and that derived contract's own `initialize()` is (as is standard practice) itself marked `initializer` and calls `super.initialize(...)`, the inner `initializer` modifier on the base's `initialize` will make the whole initialization revert.

### Impact Explanation
Any team building a derived cross-chain token app on top of these base contracts (which are shipped in the SDK specifically to be inherited, given the `virtual` markers and the "for derived contracts" NatSpec) cannot compose the standard two-level `initializer`/`onlyInitializing` OpenZeppelin pattern. Attempting the conventional inheritance-initialization idiom causes deployment/initialization of the derived bridge application to permanently fail (or forces the derived contract to skip calling the base `initialize`, bypassing `__ERC20_init`/`__Ownable_init`/`__Pausable_init` setup, which would leave the deployed token application unconfigured / uninitialized as an ERC20/Ownable/Pausable contract). This blocks correct rollout of new token-bridge routes, consistent with the "route unable to deliver messages" acceptance criterion, since a mis-initialized or unusable bridge deployment cannot function as an ISMP application.

### Likelihood Explanation
This is a design-level correctness issue in a base contract intended for reuse across every new `HyperFungibleTokenUpgradeable`/`WrappedHyperFungibleTokenUpgradeable`-based deployment. It manifests deterministically the moment a derived contract follows the standard OpenZeppelin composition pattern (`initializer` in the child calling `super.initialize`), which is the documented/expected usage given the `virtual` modifier and inheritance-oriented NatSpec.

### Recommendation
Change the outer `initialize` functions in both `HyperFungibleTokenUpgradeable.sol` and `WrappedHyperFungibleTokenUpgradeable.sol` from `initializer` to `onlyInitializing`, matching the pattern already used for their `__..._init` helpers, so a most-derived concrete contract's own `initializer`-guarded `initialize` can safely call these base initializers:
```diff
- function initialize(string memory name, string memory symbol, address initialOwner) public virtual initializer {
+ function initialize(string memory name, string memory symbol, address initialOwner) public virtual onlyInitializing {
      __HyperFungibleToken_init(name, symbol, initialOwner);
  }
```
and analogously for `WrappedHyperFungibleTokenUpgradeable.initialize`. If these base contracts are meant to also be deployed standalone (non-inherited) via their own proxy, then a concrete, non-virtual "leaf" deployment wrapper should carry the single `initializer` guard instead.

### Proof of Concept
1. Create `contract MyToken is HyperFungibleTokenUpgradeable { function initialize(...) public override initializer { super.initialize(...); } }`.
2. Deploy `MyToken` behind a proxy and call `initialize`.
3. The outer `initializer` modifier on `HyperFungibleTokenUpgradeable.initialize` detects it is already inside an initializing context (from `MyToken.initialize`'s own `initializer`) and reverts with `Initializable.InvalidInitialization`, exactly mirroring the Remix PoC in the referenced Sherlock report for `MasterAMO`.

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleTokenUpgradeable.sol (L158-183)
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

    /**
     * @notice Initializes the inherited upgradeable modules for derived contracts
     * @param name The name of the token
     * @param symbol The symbol of the token
     * @param initialOwner The address that will own this contract
     */
    function __HyperFungibleToken_init(string memory name, string memory symbol, address initialOwner)
        internal
        virtual
        onlyInitializing
    {
        __ERC20_init(name, symbol);
        __ERC165_init();
        __Ownable_init(initialOwner);
        __Pausable_init();
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L136-152)
```text
    /**
     * @notice Initializes the contract with the given owner
     * @param initialOwner The address that will own this contract
     */
    function initialize(address initialOwner) public virtual initializer {
        __WrappedHyperFungibleToken_init(initialOwner);
    }

    /**
     * @notice Initializes the inherited upgradeable modules for derived contracts
     * @param initialOwner The address that will own this contract
     */
    function __WrappedHyperFungibleToken_init(address initialOwner) internal virtual onlyInitializing {
        __ERC165_init();
        __Ownable_init(initialOwner);
        __Pausable_init();
    }
```

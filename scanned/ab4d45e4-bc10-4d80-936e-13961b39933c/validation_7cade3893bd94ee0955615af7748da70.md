### Title
`CrossChainRateReceiver` Initializes With `rate = 0`, Causing `addSupportedToken()` to Permanently Revert Until First LayerZero Message Arrives - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

### Summary
`CrossChainRateReceiver` stores the rsETH/ETH rate in a `uint256 public rate` variable that defaults to `0` at deployment. Every pool contract's `addSupportedToken()` function guards against zero-rate oracles by reverting with `UnsupportedOracle()`. This creates an initialization ordering dependency: the admin cannot register a new LST token using a freshly deployed `CrossChainRateReceiver` as its oracle until the first LayerZero message has been relayed from L1 — mirroring the Beanstalk pattern exactly.

### Finding Description
`CrossChainRateReceiver` declares `rate` as a plain storage variable with no constructor initialization: [1](#0-0) 

`rate` is only written inside `lzReceive()`, which requires a valid LayerZero message from the configured L1 provider: [2](#0-1) 

`getRate()` returns the raw storage value with no fallback: [3](#0-2) 

Every pool variant that supports LST tokens guards `addSupportedToken()` with an explicit zero-rate check. For example, in `RSETHPoolV3`: [4](#0-3) 

The same guard appears in `RSETHPoolNoWrapper`: [5](#0-4) 

And in `RSETHPoolV3ExternalBridge._addSupportedToken()`: [6](#0-5) 

And in `RSETHPoolV3WithNativeChainBridge._addSupportedToken()`: [7](#0-6) 

The result: any governance/timelock proposal that (a) deploys a new `CrossChainRateReceiver` for a new LST and (b) calls `addSupportedToken()` in the same atomic batch will always revert, because the oracle's rate is still `0` at the moment the second step executes. The rate can only become non-zero after a separate, asynchronous LayerZero relay from L1 — which cannot be included in the same transaction or governance proposal.

### Impact Explanation
The `addSupportedToken()` call reverts unconditionally whenever the supplied oracle is a freshly deployed `CrossChainRateReceiver`. The new LST cannot be listed on the pool until a separate L1→L2 rate push has been confirmed on-chain. During that window, users cannot deposit the new LST, and any governance proposal that bundles deployment + listing in one step is permanently broken and must be re-submitted after the rate arrives. This maps to **Low — Contract fails to deliver promised returns** (the listing governance action does not complete as designed) with a potential escalation to **Medium — Temporary freezing of funds** if the pool's primary `rsETHOracle` is also a zero-rate `CrossChainRateReceiver` (division-by-zero in `viewSwapRsETHAmountAndFee` freezes all ETH deposits). [8](#0-7) 

### Likelihood Explanation
Every new L2 chain deployment follows the same pattern: deploy `CrossChainRateReceiver`, then configure the pool. The ordering issue is structural and will be hit on every new chain or new LST onboarding unless the team manually pre-pushes a rate before submitting the governance proposal. Likelihood is **moderate** — it does not require any attacker; it is triggered by the normal admin deployment flow.

### Recommendation
Initialize `CrossChainRateReceiver` with a seed rate in its constructor (analogous to `InterimRSETHOracle` which requires `initRate >= 1e18` at construction): [9](#0-8) 

Alternatively, add a privileged `setInitialRate(uint256)` function that can be called once before the first `lzReceive`, or split the governance proposal into two sequential steps: (1) deploy oracle and push initial rate, (2) call `addSupportedToken()` only after confirming `getRate() > 0`.

### Proof of Concept
1. Deploy a new `CrossChainRateReceiver` for a new LST (e.g., `cbETH`). `rate == 0`.
2. In the same governance/timelock transaction, call `RSETHPoolV3.addSupportedToken(cbETH, crossChainRateReceiver, bridge)`.
3. Inside `addSupportedToken`, `IOracle(crossChainRateReceiver).getRate()` returns `0`.
4. The check `if (IOracle(oracle).getRate() == 0) { revert UnsupportedOracle(); }` fires.
5. The entire transaction reverts. The new token cannot be listed until a separate LayerZero relay from L1 updates `rate` to a non-zero value, requiring a second governance proposal. [1](#0-0) [10](#0-9)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-13)
```text
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-236)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
```

**File:** contracts/pools/RSETHPoolV3.sol (L541-554)
```text
    function addSupportedToken(address token, address oracle) external onlyRole(TIMELOCK_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        UtilLib.checkNonZeroAddress(oracle);

        if (supportedTokenOracle[token] != address(0)) {
            revert AlreadySupportedToken();
        }
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenList.push(token);
        supportedTokenOracle[token] = oracle;

        emit AddSupportedToken(token);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L584-586)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L893-895)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L699-701)
```text
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
```

**File:** contracts/pools/oracle/InterimRSETHOracle.sol (L27-32)
```text
    constructor(address admin, uint256 initRate) {
        UtilLib.checkNonZeroAddress(admin);
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(MANAGER_ROLE, admin);
        _setRate(initRate);
    }
```

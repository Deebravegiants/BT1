### Title
No `setSupportedTokenOracle` Update Mechanism in AGETHPoolV3 Locks Incorrect Token Oracle Permanently - (File: contracts/agETH/AGETHPoolV3.sol)

### Summary
`AGETHPoolV3` allows an admin to register a collateral token with an oracle via `addSupportedToken`, but provides no function to update that oracle after registration. If a wrong oracle address is supplied, the only recovery path — `removeSupportedToken` — is blocked whenever the contract holds any token balance. Every other pool variant in the codebase (`RSETHPoolV3`, `RSETHPool`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) has already been patched with a `setSupportedTokenOracle` function; `AGETHPoolV3` is the sole contract that was not updated.

### Finding Description
`addSupportedToken` in `AGETHPoolV3` writes `supportedTokenOracle[token] = oracle` and then guards against re-entry with `if (supportedTokenOracle[token] != address(0)) revert AlreadySupportedToken()`. [1](#0-0) 

There is no `setSupportedTokenOracle` function anywhere in the contract (the file ends at line 300). [2](#0-1) 

The only removal path is `removeSupportedToken`, which hard-reverts if the contract holds any balance of the token: [3](#0-2) 

The oracle value is consumed directly in the swap pricing formula:

```
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
``` [4](#0-3) 

Every sibling pool contract has already received a `setSupportedTokenOracle` correction endpoint — for example `RSETHPoolV3`: [5](#0-4) 

`AGETHPoolV3` was not updated in the same pass.

### Impact Explanation
If an incorrect oracle is registered for a collateral token:

- **Over-valued oracle** (rate too high): every depositor receives more agETH than the deposited collateral is worth, draining the protocol's backing and causing insolvency — matching the *Critical: Protocol insolvency* or *High: Theft of unclaimed yield* impact tiers.
- **Under-valued oracle** (rate too low): depositors receive fewer agETH tokens than owed — matching the *Low: Contract fails to deliver promised returns* tier.

Once any user deposits the affected token, `removeSupportedToken` is permanently blocked by the non-zero balance check, so the misconfiguration cannot be corrected without a contract upgrade.

### Likelihood Explanation
Likelihood is low-to-medium. It requires an admin to supply a wrong oracle address to `addSupportedToken`. This is an operational mistake, not an attacker action, but it is the exact same class of mistake the original Connext report identified. The risk is elevated because `AGETHPoolV3` is deployed on multiple chains (Scroll, Linea — visible in `README.md`) and each deployment is an independent opportunity for the mistake to occur.

### Recommendation
Add a `setSupportedTokenOracle` function to `AGETHPoolV3`, mirroring the pattern already present in every other pool variant:

```solidity
function setSupportedTokenOracle(
    address token,
    address oracle
) external onlyRole(DEFAULT_ADMIN_ROLE) onlySupportedToken(token) {
    UtilLib.checkNonZeroAddress(oracle);
    if (IOracle(oracle).getRate() == 0) revert UnsupportedOracle();
    supportedTokenOracle[token] = oracle;
    emit TokenOracleSet(token, oracle);
}
```

### Proof of Concept

1. Admin calls `AGETHPoolV3.addSupportedToken(wstETH, badOracle)` where `badOracle.getRate()` returns a value 10× the correct rate (passes the `!= 0` guard).
2. A user calls `deposit(wstETH, 1 ether, "ref")`.
3. `viewSwapAgETHAmountAndFee` computes `tokenToETHRate = 10 × correctRate`, so `agETHAmount` is 10× what it should be.
4. Admin discovers the mistake and calls `removeSupportedToken(wstETH, 0)`.
5. The call reverts with `TokenBalanceNotZero` because `IERC20(wstETH).balanceOf(address(this)) == 1 ether`.
6. The wrong oracle is permanently locked; every subsequent depositor continues to receive 10× agETH, draining protocol backing until a contract upgrade is executed. [6](#0-5) [3](#0-2)

### Citations

**File:** contracts/agETH/AGETHPoolV3.sol (L175-195)
```text
    function viewSwapAgETHAmountAndFee(
        uint256 amount,
        address token
    )
        public
        view
        onlySupportedToken(token)
        returns (uint256 agETHAmount, uint256 fee)
    {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // rate of token in ETH
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * tokenToETHRate / agETHToETHrate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L270-300)
```text
    /// @dev Adds a supported token
    /// @param token The token address
    function addSupportedToken(address token, address oracle) external onlyRole(DEFAULT_ADMIN_ROLE) {
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
    }

    /// @dev Removes a supported token
    /// @param token The token address
    function removeSupportedToken(address token, uint256 tokenIndex) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(token);
        if (supportedTokenList[tokenIndex] != token) revert TokenNotFoundError();
        if (IERC20(token).balanceOf(address(this)) != 0) revert TokenBalanceNotZero();

        delete supportedTokenOracle[token];
        supportedTokenList[tokenIndex] = supportedTokenList[supportedTokenList.length - 1];
        supportedTokenList.pop();
        emit RemovedSupportedToken(token);
    }
}
```

**File:** contracts/pools/RSETHPoolV3.sol (L575-589)
```text
    function setSupportedTokenOracle(
        address token,
        address oracle
    )
        external
        onlyRole(TIMELOCK_ROLE)
        onlySupportedToken(token)
    {
        UtilLib.checkNonZeroAddress(oracle);
        if (IOracle(oracle).getRate() == 0) {
            revert UnsupportedOracle();
        }
        supportedTokenOracle[token] = oracle;
        emit TokenOracleSet(token, oracle);
    }
```

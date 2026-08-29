# [H] Fund Loss/Gain When There are Different Amounts of Tokens Available in Connected Vaults (Pool) During Swaps

## Summary
Severity: High
Chain: Smart contract
Component: Catalyst-Exchange
Published: 2024-02-02
Source: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/76
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x21c388ec31681c1618ae8b5c39856d9e527a8734ec1c301d04d186fe72e38fbe
**Severity:** high

**Description:**
**Description**\
Units of Liquidity as described by documentation and whitepaper, should be global in order to support pools. It is a unit of measurement that should be accounted when swapping between chains or vaults. As described in whitepaper:
>  The Unit of liquidity is not an intermediate token the user is
exposed to or requires lock and mint bridges, it is the result of a computation based on customizable independent swap curves. 

More information from documentation:
> Each Vault contains 1 or more assets and can be connected to none, one or more other vaults to allow swaps between their assets. When vaults are connected, they form a pool. Within a pool, any asset can be exchanged for any other asset.

> To facilitate swaps between different vaults, tokens are converted into the value abstraction: Units. This is done via the internal price curve of the vault. Using a cross-chain messaging layer, the Units can be transferred to any connected vaults, followed by the conversion of the Units to the desired token.

The problem arises when connected vaults starts to diverge in terms of total amount of tokens available in the pool. When this happens, swap from vault that have more tokens to vault that have less tokens make user lose funds, while swaps from vault that have less tokens to vault that have more tokens let users earn funds. While it seems like an arbitrage opportunity, it is not; because vaults that are available in the Catalyst system should be indepentently useful as described by documentation and whitepaper. 

**Attack Scenario**\
One can create so many scenarios and exploit all of them with ease with the information provided above. To be simplistic I will use the ExampleTest.t.sol and will do just a little modification to it to show the problem.

Let's go step by step and start with setUp:
```solidity
  function setUp() public override {
    // Calls setup() on testCommon
    super.setUp();

    // Create relevant arrays for the vault.
    uint256 numTokens = 2;
    address[] memory assets = new address[](numTokens);
    uint256[] memory init_balances = new uint256[](numTokens);
    uint256[] memory weights = new uint256[](numTokens);

    // Deploy a token
    assets[0] = address(new Token("TEST", "TEST", 18, 1e6));
    init_balances[0] = 1000 * 1e18;
    weights[0] = 1;
    // Deploy another token
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Catalyst-Exchange-0x3026c1ea29bf1280f99b41934b2cb65d053c9db4/issues/76_

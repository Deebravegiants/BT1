# [M] Possible Sandwich/MEV For Reduced Gains

## Summary
Severity: Medium
Contest weight: 0.4624
Dataset id: 11781
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.3, the BTC+ protocol is architecturally designed to have a common standard APIs including mint(), redeem(), as well as harvest(). In the following, we examine the logic behind harvest() operation for yield collection. To elaborate, we show below the harvest() function in the VenusBTC+ contract. It basically harvests additional yield from the investment by converting rewards back to vBTC+.
```solidity
function harvest()
    public
    virtual
    override
    onlyStrategist
{
    // Harvest from Venus comptroller
    IVenusComptroller(VENUS_COMPTROLLER).claimVenus(address(this));
    // Harvest from VAI controller
    IVAIVault(VAI_VAULT).claim();
    uint256 _venus = IERC20Upgradeable(VENUS).balanceOf(address(this));
    // PancakeSawp : XVS --> WBNB --> BTCB
    if (_venus > 0) {
        IERC20Upgradeable(VENUS).safeApprove(PANCAKE_SWAP_ROUTER, 0);
        IERC20Upgradeable(VENUS).safeApprove(PANCAKE_SWAP_ROUTER, _venus);
        address[] memory _path = new address[](3);
        _path[0] = VENUS;
        _path[1] = WBNB;
        _path[2] = BTCB;
        IUniswapRouter(PANCAKE_SWAP_ROUTER).swapExactTokensForTokens(_venus, uint256(0), _path, address(this), block.timestamp.add(1800));
    }
    // Venus: BTCB --> vBTC
    uint256 _btcb = IERC20Upgradeable(BTCB).balanceOf(address(this));
    if (_btcb == 0)
        return;
    // If there is performance fee , charged in BTCB
    uint256 _fee = 0;
    if (performanceFee > 0)
        _fee = _btcb.mul(performanceFee).div(PERCENT_MAX);
    IERC20Upgradeable(BTCB).safeTransfer(treasury, _fee);
    _btcb = _btcb.sub(_fee);
    IERC20Upgradeable(BTCB).safeApprove(VENUS_BTC, 0);
    IERC20Upgradeable(BTCB).safeApprove(VENUS_BTC, _btcb);
    IVToken(VENUS_BTC).mint(_btcb);
    // Reinvest to get compound yield.
    _invest();
    // Also it s a good time to rebase!
    rebase();
    emit Harvested(VENUS_BTC, _btcb, _fee);
}
```
We notice the above conversion leverages PancakeSwap in order to swap related rewards to BTCB. And the swap operation does not specify a valid restriction on possible slippage and is therefore vulnerable to possible front-running attacks, resulting in a smaller converted amount. Note other contracts, e.g., AcryptoSBTC+, AutoBTC+/AutoBTCv2+, and ForTubeBTCB+, share the same issue. Note that this is a common issue plaguing current AMM-based DEX solutions. Specifically, a large trade may be sandwiched by a preceding sell to reduce the market price, and a tailgating buy-back of the same amount plus the trade amount. Such sandwiching behavior unfortunately causes a loss and brings a smaller return as expected to the trading user or the virtual account in our case because the swap rate is lowered by the preceding sell. As a mitigation, we may consider specifying the restriction on possible slippage caused by the trade or referencing the TWAP or time-weighted average price of UniswapV2. Nevertheless, we need to acknowledge that this is largely inherent to current blockchain infrastructure and there is still a need to continue the search eﬀorts for an eﬀective defense.

## Recommendation
Develop an eﬀective mitigation to the above sandwich attack to better protect the interests of protocol users. Note that the current authenticated call to harvest() with the onlyStrategist modifier mitigates this issue.

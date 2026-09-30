# [M] Proper harvest() In BadgerRenCRV+

## Summary
Severity: Medium
Contest weight: 0.4594
Dataset id: 11768
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BTC+ protocol is architecturally designed to have a common standard APIs including mint(), redeem(), and harvest(). The mint() operation allows for users to deposit BTC-pegged tokens to get BTC+ tokens, which can then later redeem()ed. The harvest() operation enables the yield collection. In the following, we examine a speciﬁc harvest() implementation of the BadgerRenCRV+ contract. To elaborate, we show below the harvest() routine. It is designed to ﬁrstly harvest from Badger Tree, then convert the collected BADGER/DIGG rewards to WBTC, next deposit WBTC to the Ren Curve pool to get the renCrv share, which is further converted to brenCrv, and ﬁnally perform the invest and rebase operations. It comes to our attention that the conversion of DIGG to WBTC is taking an incorrect conversion path, which could revert the harvest() operation. Speciﬁcally, the currently used conversion path is DIGG->WBTC->address(0) (lines 110-112) and a proper conversion path should be DIGG->WETH->WBTC.

```solidity
function harvest(address[] calldata _tokens, uint256[] calldata _cumulativeAmounts, uint256 _index, uint256 _cycle, bytes32[] calldata _merkleProof) public virtual onlyStrategist {
    // 1. Harvest from Badger Tree
    IBadgerTree(BADGER_TREE).claim(_tokens, _cumulativeAmounts, _index, _cycle, _merkleProof);
    // 2. Badger --> WETH --> WBTC
    uint256 _badger = IERC20Upgradeable(BADGER).balanceOf(address(this));
    if (_badger > 0) {
        IERC20Upgradeable(BADGER).safeApprove(UNISWAP, 0);
        IERC20Upgradeable(BADGER).safeApprove(UNISWAP, _badger);
        address[] memory _path = new address[](3);
        _path[0] = BADGER;
        _path[1] = WETH;
        _path[2] = WBTC;
        IUniswapRouter(UNISWAP).swapExactTokensForTokens(_badger, uint256(0), _path, address(this), block.timestamp.add(1800));
    }
    // 3: Digg --> WBTC
    uint256 _digg = IERC20Upgradeable(DIGG).balanceOf(address(this));
    if (_digg > 0) {
        IERC20Upgradeable(DIGG).safeApprove(UNISWAP, 0);
        IERC20Upgradeable(DIGG).safeApprove(UNISWAP, _digg);
        address[] memory _path = new address[](3);
        _path[0] = DIGG;
        _path[1] = WBTC;
        IUniswapRouter(UNISWAP).swapExactTokensForTokens(_digg, uint256(0), _path, address(this), block.timestamp.add(1800));
    }
    // ...
}
```

## Recommendation
Correct the conversion path from DIGG to WBTC in the aﬀected harvest().

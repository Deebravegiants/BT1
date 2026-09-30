# [M] Improved EOA Detection Against Front-Running of Revenue Conversion

## Summary
Severity: Medium
Contest weight: 0.6950
Dataset id: 13124
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
SushiSwap has a rather unique tokenomics around SUSHI tokens. In this section, we explore the logic behind SushiMaker and SushiBar. SushiMaker collects possible revenues (in terms of SushiSwap pairs LP tokens), convert collected revenues into SUSHI tokens, and then send them to SushiBar. SUSHI holders can stake their SUSHI assets to SushiBar to earn more SUSHI.

```solidity
function convert(address token0, address token1) public {
    // At least we try to make front-running harder to do.
    require(!Address.isContract(msg.sender), "do not convert from contract");
    IUniswapV2Pair pair = IUniswapV2Pair(factory.getPair(token0, token1));
    pair.transfer(address(pair), pair.balanceOf(address(this)));
    pair.burn(address(this));
    uint256 wethAmount = _toWETH(token0) + _toWETH(token1);
    _toSUSHI(wethAmount);
}
```

The conversion of collected revenues into SUSHI is implemented in convert(). Due to possible revenues into SushiMaker, this routine could be a target for front-running (and further facilitated by flash loans) to steal the majority of collected revenues, resulting in a loss for current stakers in SushiBar.

Conﬁdential

As a defense mechanism, SushiMaker takes a pro-active measure by only allowing EOA accounts when the revenues are being converted. The detection of whether the transaction sender is an EOA or contract is based on the isContract() routine borrowed from the Address library (shown below).

* @dev Returns true if account is a contract.
* [IMPORTANT]
* ====
* It is unsafe to assume that an address for which this function returns false is an externally-owned account (EOA) and not a contract.
* Among others, isContract will return false for the following types of addresses:
- an externally-owned account
- a contract construction
- an address where a contract will be created
- an address where a contract lived, but was destroyed
* ====

```solidity
function isContract(address account) internal view returns(bool) {
    // This method relies in extcodesize, which returns 0 for contracts
    // construction, since the code is only stored at the end of the
    // constructor execution.
    uint256 size;
    // solhint-disable-next-line no-inline-assembly
    assembly {
        size := extcodesize(account)
    }
    return size > 0;
}
```

The current isContract() could achieve its goal in most cases. However, as mentioned in the library documentation, it is unsafe to assume that an address for which this function returns false is an externally-owned account (EOA) and not a contract. Considering the speciﬁc context SushiMaker, we need a reliable method to detect the convert() transaction sender is an externally-owned account, i.e., EOA. With that, we can simply achieve our goal by require(msg.sender==tx.origin, "do not convert from contract").

## Recommendation
Apply the improved detection logic in the convert() routine as follows.

```solidity
function convert(address token0, address token1) public {
    // At least we try to make front-running harder to do.
    require(msg.sender == tx.origin, "do not convert from contract");
    IUniswapV2Pair pair = IUniswapV2Pair(factory.getPair(token0, token1));
    pair.transfer(address(pair), pair.balanceOf(address(this)));
    pair.burn(address(this));
    uint256 wethAmount = _toWETH(token0) + _toWETH(token1);
    _toSUSHI(wethAmount);
}
```

Conﬁdential

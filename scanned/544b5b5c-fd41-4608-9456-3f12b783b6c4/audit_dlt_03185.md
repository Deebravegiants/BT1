# [H] Mitigation Confirmed for H-06

## Summary
Severity: High
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/40
Type: code-finding

## Details
# MITIGATION IS NOT CONFIRMED
# MITIGATION IS NOT CONFIRMED

# Mitigation of H-06: Issue not mitigated

Link to Issue: https://github.com/code-423n4/2023-03-asymmetry-findings/issues/588

## Comments

Issue H-06 describes the potential problems of assuming a peg of stETH to ETH. The sponsor proposed a mitigation to fetch the price of stETH using a Chainlink price feed. 

While the main idea of using Chainlink as the price oracle instead of assuming a 1:1 peg is ok, there is an error in the mitigation as the change misses a critical place where the peg is still assumed. This error is described below.

There is also new issue introduced with the usage of Chainlink, which is described in a separate report ([adriro-NEW-H-02])

## Technical Details

The proposed pull request changes the implementation of the `ethPerDerivative()` function to fetch the stETH price using Chainlink. However, as we can see in the following snippet, the `withdraw()` function is still assuming a peg of stETH to ETH:

https://github.com/asymmetryfinance/smart-contracts/pull/242/files#diff-ac281bf63004ef9a825c084018c54f10b03233cd4f286398f5d5e993612308b5R60-R71

```solidity
function withdraw(uint256 _amount) external onlyOwner {
    IWStETH(WST_ETH).unwrap(_amount);
    uint256 stEthBal = IERC20(STETH_TOKEN).balanceOf(address(this));
    IERC20(STETH_TOKEN).approve(LIDO_CRV_POOL, stEthBal);
    uint256 minOut = (stEthBal * (10 ** 18 - maxSlippage)) / 10 ** 18;
    IStEthEthPool(LIDO_CRV_POOL).exchange(1, 0, stEthBal, minOut);
    // solhint-disable-next-line
    (bool sent, ) = address(msg.sender).call{value: address(this).balance}(
        ""
    );
    require(sent, "Failed to send Ether");
}
```

The calculation of `minOut` is applying the slippage directly to the `stEthBal` variable, which is the stETH amount. This means that this calculation is assuming a 1:1 peg (see original report in H-06 for a more detailed explanation).


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/40_

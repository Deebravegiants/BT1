# [H] `removeFromAllTicks` should be done before `getTVL`

## Summary
Severity: High
Chain: Smart contract
Component: 2023-09-goodentry-mitigation
Published: 2023-09-11
Source: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/57
Type: code-finding

## Details
# Lines of code

https://github.com/GoodEntry-io/ge/blob/c7c7de57902e11e66c8186d93c5bb511b53a45b8/contracts/GeVault.sol#L265-L293


# Vulnerability details

After the mitigation, the TR fee is directly sent to GE vault. Suppose 0.1 eth trading fee has accumulated in TR.

    uint vaultValueX8 = getTVL();   
    uint adjBaseFee = getAdjustedBaseFee(token == address(token0));
    // Wrap if necessary and deposit here
    if (msg.value > 0){
      require(token == address(WETH), "GEV: Invalid Weth");
      // wraps ETH by sending to the wrapper that sends back WETH
      WETH.deposit{value: msg.value}();
      amount = msg.value;
    }
    else { 
      ERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    }
    
    // Send deposit fee to treasury
    uint fee = amount * adjBaseFee / 1e4;
    ERC20(token).safeTransfer(treasury, fee);
    uint valueX8 = oracle.getAssetPrice(token) * (amount - fee) / 10**ERC20(token).decimals();


    require(tvlCap > valueX8 + vaultValueX8, "GEV: Max Cap Reached");


    uint tSupply = totalSupply();
    // initial liquidity at 1e18 token ~ $1
    if (tSupply == 0 || vaultValueX8 == 0)
      liquidity = valueX8 * 1e10;
    else {
      liquidity = tSupply * valueX8 / vaultValueX8;
    }

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-goodentry-mitigation-findings/issues/57_

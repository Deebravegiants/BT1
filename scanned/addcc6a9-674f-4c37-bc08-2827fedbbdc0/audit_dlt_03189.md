# [H] Mitigation Confirmed for NEW

## Summary
Severity: High
Chain: Smart contract
Component: 2023-05-asymmetry-mitigation
Published: 2023-05-08
Source: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/13
Type: code-finding

## Details
Note: Issue has not actually been resolved but for some reason I can't get my issues to submit without "Mitigation confirmed (no new vulnerabilities detected)" checked so I am doing this as a work around

## Severity

Medium

## Lines of code

https://github.com/asymmetryfinance/smart-contracts/pull/242/files#diff-ac281bf63004ef9a825c084018c54f10b03233cd4f286398f5d5e993612308b5L56-L67

## Impact

Contract still assumes 1:1 peg for stETH in WstETH#withdraw leading to ineffective slippage calculations

## Proof of Concept

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

Above we can see that when calculating minOut, the contract still assumes a 1:1 peg of stETH because it doesn't adjust minOut by the price of stETH.

This will lead to ineffective slippage protection when stETH isn't at a 1:1 peg.

Example:
Assume slippage = 1%. If stETH were to depeg to 0.98. When swapping it would try to make sure that the user received at least 0.99 ETH. Whenever trying to swap it will now revert. 

## Tools Used


_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-05-asymmetry-mitigation-findings/issues/13_

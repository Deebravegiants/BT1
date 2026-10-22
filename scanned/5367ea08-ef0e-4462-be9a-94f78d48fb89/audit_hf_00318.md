# [M] `USDMPegRecovery.sol#provide

## Summary
Severity: Medium
Contest weight: 0.1903
Dataset id: 1565
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[USDMPegRecovery.sol#L73-L82](https://github.com/code-423n4/2022-02-concur/blob/02d286253cd5570d4e595527618366f77627cdaf/contracts/USDMPegRecovery.sol#L73-L82)  

    function provide(uint256 _minimumLP) external onlyGuardian {
        require(usdm.balanceOf(address(this)) >= totalLiquidity.usdm, "<liquidity");
        // truncate amounts under step
        uint256 addingLiquidity = (usdm.balanceOf(address(this)) / step) * step;
        // match usdm : pool3 = 1 : 1
        uint256[2] memory amounts = [addingLiquidity, addingLiquidity];
        usdm.approve(address(usdm3crv), addingLiquidity);
        pool3.approve(address(usdm3crv), addingLiquidity);
        usdm3crv.add_liquidity(amounts, _minimumLP);
    }

In the current implementation of `USDMPegRecovery.sol#provide()`, `addingLiquidity` is calculated solely based on `usdm` balance (truncate at a step of 250k), and it always uses the same amount of 3pool tokens to add_liquidity with.

Based on other functions of the contract, the balance of `usdm` can usually be more than the `pool3` balance, in that case, `usdm3crv.add_liquidity()` will fail.

## Recommendation
Change to:
    
    function provide(uint256 _minimumLP) external onlyGuardian {
        require(usdm.balanceOf(address(this)) >= totalLiquidity.usdm, "<liquidity");
        uint256 tokenBalance = Math.min(usdm.balanceOf(address(this)), pool3.balanceOf(address(this)));
        // truncate amounts under step
        uint256 addingLiquidity = (tokenBalance / step) * step;
        // match usdm : pool3 = 1 : 1
        uint256[2] memory amounts = [addingLiquidity, addingLiquidity];
        usdm.approve(address(usdm3crv), addingLiquidity);
        pool3.approve(address(usdm3crv), addingLiquidity);
        usdm3crv.add_liquidity(amounts, _minimumLP);
    }

I agree with the finding, ultimately liquidity addition won’t be at a 1:1 rate and the code won’t adapt to that situation causing reverts.

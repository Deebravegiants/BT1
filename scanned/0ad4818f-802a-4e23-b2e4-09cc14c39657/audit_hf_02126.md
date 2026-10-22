# [H] Inconsistent Fee Rate Between PancakeSwap And DjinnAutoBuyer

## Summary
Severity: High
Contest weight: 0.6143
Dataset id: 11931
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned in Section 3.2, the DjinnAutoBuyer contract has a helper routine, i.e., buyTokenFixed(), that is designed to swap tokens. It takes BNB and uses PancakeSwap's BUSD-WBNB and DJINN-BUSD pairs to swap the fee token DJINN. However, it comes to our attention that the fee rate using in the PancakeSwap BUSD-WBNB pair (lpWbnbBusd : 0.2%) is different from the fee rate using in DjinnAutoBuyer (SWAP_PERMILLION_PCS2 : 0.25%). The inconsistent fee rate between PancakeSwap and DjinnAutoBuyer will lead to more BNB spend for the same amount of fee tokens.
```solidity
contract DjinnAutoBuyer
    using SafeERC20 for IERC20;
    using Address for address;
    using SafeMath for uint256;

    // DATA STRUCTURES
    // PUBLIC CONSTANT VARIABLES
    // swap contracts
    address public constant lpDjinnBusd = 0x03962E1907B0FA72768Bd865e8cA0C45C7De4937;
    address public constant lpWbnbBusd = 0x1B96B92314C44b159149f7E0303511fB2Fc4774f;
    address public constant wbnbToken = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;

    // factor for swap fees
    uint256 public constant SWAP_PERMILLION_PCS1 = 998000;
    uint256 public constant SWAP_PERMILLION_PCS2 = 997500;

    function buyTokenFixed(
        uint256 _amountOut,
        address _outTarget,
        address _refundTarget
    ) external payable returns (uint256) {
        uint256 _amountInBusd = amountIn(lpDjinnBusd, false, _amountOut, SWAP_PERMILLION_PCS1);
        uint256 _amountInWbnb = amountIn(lpWbnbBusd, true, _amountInBusd, SWAP_PERMILLION_PCS2);
    }
}
```
Note another function buyTokenFromBnb() from the same contract shares the same issue.

## Recommendation
We suggest to make the BUSD-WBNB fee rate consistent between PancakeSwap and DjinnAutoBuyer.

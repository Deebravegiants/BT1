# [M] Possible Costly LPs From Improper BankingNode Initialization

## Summary
Severity: Medium
Contest weight: 0.4629
Dataset id: 11746
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BankingNode contract allows the lenders to deposit their funds to receive bUSD token as shares. The lenders will get their pro-rata share based on their deposited amount. While examining the share calculation with the given deposits, we notice an issue that may unnecessarily make the share extremely expensive and bring hurdles (or even causes loss) for later depositors. To elaborate, we show below the deposit() routine. This deposit() routine is used for participating lenders to deposit the supported asset (e.g., baseToken) and get respective shares in return. The issue occurs when the BankingNode contract is being initialized under the assumption that the current contract is empty.

```solidity
function deposit(uint256 _amount)
external
ensureNodeActive
nonZeroInput(_amount)
{
    // check the decimals of the baseTokens
    address _baseToken = baseToken;
    uint256 decimalAdjust = 1;
    uint256 tokenDecimals = ERC20(_baseToken).decimals();
    if (tokenDecimals != 18) {
        decimalAdjust = 10**(18 - tokenDecimals);
    }
    //get the amount tokens to mint
    uint256 what = _amount * decimalAdjust;
    if (totalSupply() != 0) {
        //no need to decimal adjust here as total asset value adjusts
        // unable to deposit getTotalAssetValue() == 0 and totalSupply() != 0, but this
        // should never occur as defaults will get slashed for some base token recovery
        what = (_amount * totalSupply()) / getTotalAssetValue();
    }
    // transfer tokens from the user and mint
    TransferHelper.safeTransferFrom(
        _baseToken,
        msg.sender,
        address(this),
        _amount
    );
    _mint(msg.sender, what);
    _depositToLendingPool(_baseToken, _amount);
    emit baseTokenDeposit(msg.sender, _amount);
}
```

Specifically, when the contract is being initialized, the share value directly takes the value of _amount (line 489), supposing the decimalAdjust is 1, which is manipulatable by the malicious actor. As this is the first deposit, the current total supply equals the calculated shares = 1 WEI. With that, the actor can further deposit a huge amount of baseToken into the lendingpool contract on behalf of the BankingNode with the goal of making the share extremely expensive. An extremely expensive share can be very inconvenient to use as a small number of 1 Wei may denote a large value. Furthermore, it can lead to precision issue in truncating the computed pool tokens for deposited assets. If truncated to be zero, the deposited assets are essentially considered dust and kept by the pool without returning any pool tokens. This is a known issue that has been mitigated in popular Uniswap. When providing the initial liquidity to the contract (i.e. when totalSupply is 0), the liquidity provider must sacrifice 1000 LP tokens (by sending them to address(0)). By doing so, we can ensure the granularity of the LP tokens is always at least 1000 and the malicious actor is not the sole holder. This approach may bring an additional cost for the initial liquidity provider, but this cost is expected to be low and acceptable.

## Recommendation
Revise current execution logic of share calculation to defensively calculate the share amount when the pool is being initialized. An alternative solution is to ensure guarded launch that safeguards the first deposit to avoid being manipulated.

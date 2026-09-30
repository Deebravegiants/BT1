# [C] Improper Approval to Drain Market Funds in CErc20

## Summary
Severity: Critical
Contest weight: 0.5851
Dataset id: 12690
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Each asset supported by the Paxo protocol is integrated through a so-called CToken contract, which is an ERC20 compliant representation of balances supplied to the protocol. By minting CTokens, users can earn interest through the CToken s exchange rate, which increases in value relative to the underlying asset, and further gain the ability to use CTokens as collateral. While examining the exposed functions in the CToken-inherited CErc20, we notice one particular one puts the pool funds at risk. To elaborate, we show below the related function increaseMarketAllowance(). As the name indicates, this function is used to increase the market allowance. However, it comes to our attention that the given input asset (line 304) is not validated, which may be exploited to grant spend allowance to the given input asset. And the given input asset address may not be trusted!
```solidity
function getCTokenUnderlying(address cToken) view internal returns (address) {
    return CTokenU(cToken).underlying();
}

function increaseMarketAllowance(address asset) external {
    EIP20Interface(getCTokenUnderlying(asset)).approve(asset, type(uint).max);
}
```

## Recommendation
Validate the input asset in the above increaseMarketAllowance() routine.

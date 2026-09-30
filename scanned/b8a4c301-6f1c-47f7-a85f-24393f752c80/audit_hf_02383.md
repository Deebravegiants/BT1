# [M] Revisited Bridge Fee Calculation in RadiantOFT::_getBridgeFee()

## Summary
Severity: Medium
Contest weight: 0.4520
Dataset id: 12858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RadiantOFT contract implements an OFT-20 token (i.e., NOVA) based on the LayerZero, which is the Radiant's native utility token. The LayerZero Labs's Omnichain Fungible Token (i.e., OFT) interoperability solution enables native, cross-chain token transfers. With LayerZero's guarantee of valid delivery, the token is burned on the source chain and minted on the destination chain directly through the token contract. In particular, the Radiant V2 protocol will charge a certain amount of native token (e.g., ETH) as bridge fee during cross-chain token transfers. The _getBridgeFee() routine is designed to calculate the bridge fee. While examining its logic, we observe its current implementation needs to be improved. To elaborate, we show below the related code snippet of the RadiantOFT contract. By design, the amount of the bridge fee is related to the value of the cross-chain token. Inside the _getBridgeFee() routine, the getTokenPrice() routine is called (line 128) to retrieve the price of the token against ETH. The statement of rdntAmount.mul(10**priceDecimals).div(priceInEth).mul(10**18).div(10**_decimals) (line 130) is designed to measure the value of the cross-chain token against ETH. Apparently, it does not meet the requirement. We suggest to improve the implementation as below: rdntAmount.mul(priceInEth).div(10**priceDecimals).mul(10**18).div(10**_decimals) (line 130).

```solidity
function _getBridgeFee(uint256 rdntAmount) internal view returns (uint256) {
    if (address(priceProvider) == address(0)) {
        return 0;
    }
    uint256 priceInEth = priceProvider.getTokenPrice(true);
    uint256 priceDecimals = priceProvider.decimals();
    uint256 rdntInEth = rdntAmount.mul(10**priceDecimals).div(priceInEth).mul(10**18).div(10**_decimals);
    return rdntInEth.mul(FEE_BRIDGING).div(FEE_DIVISOR);
}
```

## Recommendation
Properly calculate the value of the cross-chain token inside the _getBridgeFee() routine.

# [C] Lack Of Authentication For Privilege Functions

## Summary
Severity: Critical
Contest weight: 0.5883
Dataset id: 11775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the BSD protocol, the owner account plays a critical role in governing and regulating the entire operation and maintenance (e.g., price setting). It also has the privilege to transfer funds from the polPoolAddr, the pusdPoolAddr, and the pnxPoolAddr to any addresses. To elaborate, we show below the related setPOLPrice() function.

```solidity
function setPOLPrice(uint256 amount) public {
    _polPrice = amount;
}
```

As we can see in the function above, this function is deﬁned with a public modiﬁer. The same issue is also present for the setMinted(), setStaked(), setBonus(), setBonusAvailable(), setWaitingBurn(), setBonusRate(), setStakeRate(), setPUSDPrice(), setPNXPrice(), transferPOLTo(), transferPUSDTo(), and transferPNXTo() functions in the PolDataMain contract. Besides, the transferPOLTo(), transferPUSDTo(), and transferPNXTo() functions in the PolMain contract also have the same issue. These privileged functions require proper authentication, which is currently missing. Malicious users are able to call some of these functions to change these important settings and may further transfer all the funds in polPoolAddr, pusdPoolAddr, and pnxPoolAddr to their own accounts.

## Recommendation
Add necessary authentication to the functions mentioned above, e.g., the onlyOwner modiﬁer.

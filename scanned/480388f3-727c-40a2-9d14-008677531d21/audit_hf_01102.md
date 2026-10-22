# [M] Automate liquidity migration actions to mitigate human error

## Summary
Severity: Medium
Contest weight: 0.2119
Dataset id: 4221
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The BondingCurve contract's buy function is designed to facilitate the purchase of tokens along a bonding curve, adjusting the token supply and price dynamically based on demand. Currently, when the bonding curve is completed, the function emits an event and relies on manual intervention by an administrator to proceed with subsequent actions. This manual process introduces potential for human error and delays. For example, if enableTrading is triggered before the bonding curve is fully funded and its ethers sent to the token contract, it will prevent any subsequent attempts to call addLiquidity once the funds from the bonding curve are received. To avoid locking funds, an admin would need to intervene by using the withdrawStuckTokens function. To automate the process, the transferAll function, which is responsible for transferring all Ether and burning residual tokens, should be automatically invoked upon the completion of the bonding curve. Furthermore, the TokenContract's enableTrading function, which activates trading, should be called automatically at the end of transferAll's execution. This function should be restricted to be callable only by the BondingCurve contract, rather than the owner, to ensure a seamless transition and reduce the risk of administrative errors.

## Recommendation
To enhance the reliability and security of the protocol, it is recommended to automate the liquidity migration actions currently requiring manual intervention. Modify the BondingCurve contract to automatically call the transferAll function internally when the bonding curve is completed, thereby eliminating the need for an event-based manual trigger. Additionally, adjust the transferAll function to automatically invoke the TokenContract.enableTrading function upon completion. Ensure that BondingCurve.transferAll is set as internal, and that TokenContract.enableTrading is callable only by the BondingCurve contract to prevent unauthorized access and maintain the integrity of the protocol's operational flow. This automation will streamline the process, reduce the potential for human error, and ensure a more secure and efficient transition from bonding curve completion to active trading.

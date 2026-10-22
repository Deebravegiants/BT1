# [M] Changing a strategy can be bricked

## Summary
Severity: Medium
Contest weight: 0.4317
Dataset id: 1466
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability arises in a vault contract that only permits a strategy to be replaced when the strategy reports zero invested assets. The invested assets are calculated as the sum of the strategy’s raw aUST token balance and any pending redemption amounts. Because the check uses the on‑chain aUST balance directly, an attacker can send a tiny amount of aUST (for example, 1 wei) directly to the strategy contract. Once any external aUST resides in the strategy, the investedAssets value becomes non‑zero, so the vault’s setStrategy function reverts and the current strategy cannot be swapped out. This creates a griefing scenario where the protocol becomes effectively bricked: the intended upgrade or replacement of the strategy is blocked, and the vault is forced to attempt a redemption of the offending aUST. However, EthAnchor, which the vault interacts with, does not accept redeems of less than 10 aUST, meaning the tiny amount cannot be redeemed either. The attacker can repeat the injection of minimal aUST, keeping the balance above zero and preventing the vault from ever meeting the zero‑balance precondition for strategy change. The impact is that the protocol’s governance or operators lose the ability to upgrade the strategy, potentially freezing user deposits and impairing withdrawals, which harms token holders and any parties relying on the protocol’s correct operation. The issue was discovered during a manual audit by checking the logic of setStrategy and the definition of investedAssets in the base strategy contract; the indirect reliance on raw token balances made the bug subtle and easy to overlook in testing, especially because normal operation rarely involves external token transfers to the strategy. From a user perspective the UI may still display an option to change the strategy, but the transaction will revert with an error, leading to confusion as funds appear to be stuck and no new strategy can be deployed. The root cause is the mismatch between internal accounting (deposits and pending redeems) and external token balances, combined with the lack of a mechanism for the strategy to return aUST to the vault. To remediate, the contract should maintain an internal accounting of aUST held by the strategy, update this accounting on every deposit and redemption, and use the internal figure—not the raw token balance—to decide whether the strategy is empty. Additionally, the strategy should be given the ability to transfer any aUST it holds back to the vault so that accidental or malicious external deposits can be cleared, ensuring that the zero‑balance requirement can be satisfied and the vault remains upgradeable.

## Proof of Concept
`setStrategy` requires `strategy.investedAssets() == 0`. [(Code ref)](https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/Vault.sol#L113:#L116) `investedAssets` contains the aUST balance and the pending redeems: [(Code ref)](https://github.com/code-423n4/2022-01-sandclock/blob/main/sandclock/contracts/strategy/BaseStrategy.sol#L271)
    
```solidity
uint256 aUstBalance = _getAUstBalance() + pendingRedeems;
```

So if a griefer sends 1 wei of aUST to the strategy before it is to be replaced, it would not be able to be replaced. The protocol would then need to redeem the aUST and wait for the process to finish - and the griefer can repeat his griefing. As they say, griefers gonna grief.

## Recommendation
Consider keeping an internal aUST balance of the strategy, which will be updated upon deposit and redeem, and use it (instead of raw aUST balance) to check if the strategy holds no aUST funds.

Another option is to add capability for the strategy to send the aUST to the vault.

Warden kenzo requested that I add the following: 

“Additionally, impact-wise: EthAnchor does not accept redeems of less than 10 aUST. This means that if a griefer only sends 1 wei aUST, the protocol would have to repeatedly send additional aUST to the strategy to be able to redeem the griefer’s aUST.”

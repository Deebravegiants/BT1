# [M] Staking module is vulnerable to ﬁrst depositor attack

## Summary
Severity: Medium
Reporter: 0xluk3, also found by trachev, chupinexx, 0xabdullah, 0xabdullah, CAUsr, Josh4324, ZanyBonzy, 0xb0k0 and Joshuajee
Contest weight: 0.4949
Dataset id: 4929
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Staking module, which forks SushiBar contract (a simpler predecessor of
ERC4626 vault), uses the formula amount * total_x_token / total_token_in_pool to calculate shares
minted to a user (or the exact amount of deposited tokens if there are no deposits already). This is done
in the operations.rell#L59-L69.
While the exchange rate mechanism is designed to accrue value of shares as tokens are deposited to the
treasury, it creates a vulnerability where the ﬁrst depositor can manipulate the exchange rate by donating
funds to the treasury, allowing them to claim an unfair proportion of shares.
Although the transfer() function protects against sending 0 amounts, which reduces the impact of the
classic inﬂation attack, it's still possible to manipulate the exchange rate, just to a lesser degree.

Impact Explanation:
High -- user funds may be partially stolen. A malicious ﬁrst depositor can extract
signiﬁcant value from subsequent depositors.

## Proof of Concept
The vulnerability exists in the share calculation logic:
```solidity
if (total_x_token == 0 or total_token_in_pool == 0) {
    assets.Unsafe.mint(caller, mapping_token_and_x_token.x_token, amount);
    amount_x_token = amount;
} else {
    amount_x_token = amount * total_x_token / total_token_in_pool;
    assets.Unsafe.mint(caller, mapping_token_and_x_token.x_token, amount_x_token);
}
```
The transfer does not allow for minting 0 shares by default, however the attack is still possible to inﬂate
the exchange rate by donating amount of tokens to the treasury as the ﬁrst depositor. As the resulting
shares will be rounded down, the attacker may proﬁt from the inﬂated exchange rate:
Attack scenario:
• Alice deposits 1 token, gets 1 x-token. Exchange rate is 1.
• Alice donates 19,999 tokens. Exchange rate is inﬂated to 1:20000.
• Bob deposits 25,000 tokens, gets 25,000 * 1 / 20,000 = 1.25 x-tokens Which gets rounded down
to 1.
• Total pool: 45,000 tokens, total x-tokens: 2.
• Alice redeems 1 x-token for 45,000 * 1/2 = 22,500 tokens.
• Alice proﬁts slightly, while Bob receives less value than deposited.

## Recommendation
Several mitigation strategies are available:
• Implement "dead shares" approach used in Uniswap V2 by minting an initial amount of shares to
dead/neutral address.
• Enforce a minimum amount of deposit.
• Track balances internally rather than relying on direct balance checks. This, however, may increase
complexity.
The simplest approach would be adopting the Uniswap V2 method of minting dead shares during the ﬁrst
deposit.

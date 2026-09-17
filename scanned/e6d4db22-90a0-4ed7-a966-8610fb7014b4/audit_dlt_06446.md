# [M] GasToken(AZERO) might be stuck in nomination_agent contract when the pool is in destroy mode

## Summary
Severity: Medium
Chain: Smart contract
Component: Kintsu
Published: 2024-05-20
Source: https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/issues/50
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0xa1831e597d297298b9a2f85b76ebd02df7e13008d4dc569249e2a87117190381
**Severity:** medium

**Description:**
**Description**\
As stated in [Conditions for a permissionless dispatch](https://github.com/paritytech/polkadot-sdk/blob/e7b6d7dffd6459174f02598bd8b84fe4b1cb6e72/substrate/frame/nomination-pools/src/lib.rs#L2223C9-L2227), when `The pool is in destroy mode and the target is not the depositor.`, the [nomination-pools.withdraw_unbonded](https://github.com/paritytech/polkadot-sdk/blob/e7b6d7dffd6459174f02598bd8b84fe4b1cb6e72/substrate/frame/nomination-pools/src/lib.rs#L2240C10-L2357) can be called by anyone. Which consistents with [nomination-pools.ok_to_withdraw_unbonded_with](https://github.com/paritytech/polkadot-sdk/blob/e7b6d7dffd6459174f02598bd8b84fe4b1cb6e72/substrate/frame/nomination-pools/src/lib.rs#L1233-L1245) called in [nomination-pools#L2256](https://github.com/paritytech/polkadot-sdk/blob/e7b6d7dffd6459174f02598bd8b84fe4b1cb6e72/substrate/frame/nomination-pools/src/lib.rs#L2256), and at the end of `nomination-pools.withdraw_unbonded`, the GasToken(AZERO) will be transferred to `member_account` which is `nomination_agent` in our case.
Then according to `nomination_agent.nomination_agent`, the amount of GasToken(AZERO) sent to valut will be [withdrawn = after - before;](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/nomination_agent/lib.rs#L125-L130)


**Attack Scenario**\
So please consider in a case that the pool is in destroy mode, and someone else calls [nomination-pools.withdraw_unbonded](https://github.com/paritytech/polkadot-sdk/blob/e7b6d7dffd6459174f02598bd8b84fe4b1cb6e72/substrate/frame/nomination-pools/src/lib.rs#L2240-L2357) before the valut calls [nomination_agent.withdraw_unbonded](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/nomination_agent/lib.rs#L104-L133), the GasToken(AZERO) will be transferred to `nomination_agent`, and then when the vault calls [nomination_agent.withdraw_unbonded](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/nomination_agent/lib.rs#L104-L133), because the token has already be transferred to nomination_agent, the [withdrawn = after - before](https://github.com/hats-finance/Kintsu-0x7d70f9442af3a9a0a734fa6a1b4857f25518e9d2/blob/c9bdc853b18c305de832307b91a9bca0f281f71e/src/nomination_agent/lib.rs#L125C17-L125C43) will zero.

Which means that the GasToken(AZERO) won't be transferred to vault.

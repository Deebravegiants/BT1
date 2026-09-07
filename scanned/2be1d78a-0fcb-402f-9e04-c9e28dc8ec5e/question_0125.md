# Q0125: Direct route msg {"action":"deposit"} nep141:wrap.near

## Question
Using `createNearWithdrawalRoute(msg)` with msg = {"action":"deposit"} and `assetId` = `nep141:wrap.near`, can an unprivileged caller make `DirectBridge.createWithdrawalIntents` emit `ft_withdraw` with `receiver_id` = `destinationAddress` and `msg` set (so intents.near performs `ft_transfer_call`), and `min_gas` omitted, such that the receiving contract's `ft_on_transfer` refunds or redirects the tokens and the SDK still reports `completed` with the intent tx hash?

## Target
- File/function: packages/intents-sdk/src/bridges/direct-bridge/direct-bridge-utils.ts `createWithdrawIntentPrimitive`; direct-bridge.ts `createWithdrawalIntents`, `describeWithdrawal`
- Entrypoint: `IntentsSDK.processWithdrawal` with `createNearWithdrawalRoute(msg)`
- Attacker controls: `routeConfig.msg` ({"action":"deposit"}), `destinationAddress` (any NEAR account that exists), `assetId`
- Exploit idea: With `msg` present the intent becomes `ft_transfer_call`; `min_gas` is undefined; `describeWithdrawal` returns `completed` unconditionally with `args.tx.hash`. `validateWithdrawal` only checks the account exists and is not the token contract.
- Invariant to test: For a Direct withdrawal, the token balance credited to `destinationAddress` after settlement must equal `amount`; the SDK must not report completed when `ft_transfer_call` refunded.
- Expected Immunefi impact: High - status/hash misreport making an integrator credit or refund twice (HackenProof: withdrawal processing / serialization correctness)
- Fast validation: vitest: build intents and assert `msg`/`min_gas`; integration: mock relay `SETTLED` and assert `describeWithdrawal` cannot distinguish refund.

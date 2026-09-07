# Q0763: Aurora route: `auroraEngineContractId` set to an arbitrary

## Question
With `createVirtualChainRoute(...)` and `auroraEngineContractId` set to an arbitrary NEAR contract, can an unprivileged caller make `AuroraEngineBridge.createWithdrawalIntents` emit an `ft_withdraw` whose `receiver_id` and `msg` deposit the tokens into a contract or EVM address that is not the user's on the intended virtual chain, while `validateWithdrawal` only checked `validateAddress(destinationAddress, Chains.Ethereum)`?

## Target
- File/function: packages/intents-sdk/src/bridges/aurora-engine-bridge/aurora-engine-bridge-utils.ts `createWithdrawIntentPrimitive`, `makeAuroraEngineDepositMsg`; aurora-engine-bridge.ts
- Entrypoint: `IntentsSDK.processWithdrawal` with `createVirtualChainRoute`
- Attacker controls: `routeConfig.auroraEngineContractId`, `proxyTokenContractId`, `destinationAddress`
- Exploit idea: The engine and proxy contract ids are caller-supplied and unvalidated; the msg format is `<lowercase hex without 0x>` or `<engine>:<hex>`.
- Invariant to test: tokens are credited to `destinationAddress` on the virtual chain identified by a legitimate Aurora engine contract.
- Expected Immunefi impact: High - withdrawal stuck or refunded to the wrong account until manual intervention (HackenProof: withdrawal processing; Immunefi class: temporary freezing of funds)
- Fast validation: vitest: inspect produced intent for crafted routeConfig values.

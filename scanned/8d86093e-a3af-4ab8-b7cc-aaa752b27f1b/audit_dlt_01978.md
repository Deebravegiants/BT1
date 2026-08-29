# [?] Fix base bridging and a race condition in key funder (#3012)

## Summary
Severity: Unknown
Chain: Hyperlane
Component: hyperlane-xyz/hyperlane-monorepo
Published: 2023-12-01
Source: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/9fc0866b29bf2190ecb8bc0ba78c267987c4f809
Type: security-commit

## Details
Fix base bridging and a race condition in key funder (#3012)

### Description

Turns out bridging from L1 to Base has been broken the whole time :(
it's because the version of @eth-optimism/sdk we were using was 1.8.0
(according to yarn.lock) which was released in late 2022
https://github.com/ethereum-optimism/optimism/releases/tag/%40eth-optimism%2Fsdk%401.8.0,
far before Base was launched. So we'd always get this error in key
funder because we rely on the optimism SDK knowing about Base's chain
ID:
```
{"chain":"base","error":"Error: cannot get contract AddressManager for unknown L2 chain ID 8453, you must provide an address\n    at getOEContract (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/utils/contracts.ts:58:11)\n    at getAllOEContracts (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/utils/contracts.ts:121:46)\n    at new CrossChainMessenger (/hyperlane-monorepo/node_modules/@eth-optimism/sdk/src/cross-chain-messenger.ts:170:39)\n    at ContextFunder.bridgeToOptimism (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:652:33)\n    at ContextFunder.bridgeToL2 (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:637:23)\n    at processTicksAndRejections (node:internal/process/task_queues:96:5)\n    at async ContextFunder.bridgeIfL2 (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:492:9)\n    at async gracefullyHandleError (/hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:774:5)\n    at async /hyperlane-monorepo/typescript/infra/scripts/funding/fund-keys-from-deployer.ts:394:29\n    at async Promise.all (index 9)","level":"error","message":"Error bridging to L2"}
```

The fix was just to upgrade to a newer optimism SDK version

A mystery to me is that we'd get that log ^ but sometimes the key funder
pod would show as having ran successfully. My best guess here is there
was a race condition in `fund` when we had a variable local to the
function called `failureOccurred` that many promises which were
`Promise.all`'d would read and write to it via `failureOccurred ||=
await someFallibleFn()`. I changed the logic here to not have multiple
concurrent promises contend for the variable

Also made a small change to not include mantapacific in the list of
relayer keys for the Hyperlane context. It's not ever used, and had a
downstream effect of us trying to fund the Kathy key on mantapacific,
which we don't want to actually do

### Drive-by changes

n/a

### Related issues

n/a


_Trimmed to 38 lines — full report: https://github.com/hyperlane-xyz/hyperlane-monorepo/commit/9fc0866b29bf2190ecb8bc0ba78c267987c4f809_

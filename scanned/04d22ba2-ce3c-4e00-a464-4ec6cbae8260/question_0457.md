# Q457: rpc fail-open bridge parsing via RPC

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `port`, `signature`, and `origin` so that `RPC` in `libraries/sdk-rpc/src/rpc.ts` carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it, breaking the invariant that malformed RPC payloads must fail closed and never select state-changing defaults, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/sdk-rpc/src/rpc.ts::RPC
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: a metadata-bearing request plus disconnect/reconnect timing from the same browser session
- Exploit idea: carry pre-approval, unlocked, or imported-seed state across a boundary that should reset it
- Invariant to test: malformed RPC payloads must fail closed and never select state-changing defaults
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: simulate two origins or port sessions, interleave requests and responses, and assert that only the approved origin receives the intended result

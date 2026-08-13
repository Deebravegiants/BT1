# Q441: client response mix-up via createProxy

## Question
Can an unprivileged attacker enter through connected website RPC request handled by the wallet bridge and control `params`, `port`, and `method` so that `createProxy` in `libraries/sdk-rpc/src/client.ts` make one origin reach a method namespace or capability that was only approved for another origin or flow, breaking the invariant that wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: libraries/sdk-rpc/src/client.ts::createProxy
- Entrypoint: connected website RPC request handled by the wallet bridge
- Attacker controls: malformed JSON or RPC payload fields that still pass boundary parsing
- Exploit idea: make one origin reach a method namespace or capability that was only approved for another origin or flow
- Invariant to test: wallet-mutating or seed-ingesting methods must remain isolated from generic RPC capability exposure
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: simulate two origins or port sessions, interleave requests and responses, and assert that only the approved origin receives the intended result

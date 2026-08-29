# [H] EL-2026-27: bn256 scalar multiplication DELEGATECALL returns incorrect result after gnark switch

## Summary
Severity: High
Chain: Ethereum (execution layer)
Component: Geth, Erigon
Source: https://notes.ethereum.org/EpXWSoChQXyV1u1ozAH23w
Type: ef-disclosure

## Details
### Consensus flaw

Potential consensus-flaw affecting `[geth, erigon]` versus `[eels, nethermind, nimbus, evmone ,reth]` 

```
INFO [06-16|22:07:46.105] Consensus flaw                           file=/fuzztmp/00000019-mixed-1.json vm=erigonbatch-0 have=e4429992252d3f9248c5471785bf487d "ref vm"=gethbatch-0 want=647fcceb17fc6111e7763dcd853311cc
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Factory exiting
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Shortcutting through abort
INFO [06-16|22:07:46.236] Factory exiting
INFO [06-16|22:07:46.236] Factory exiting
INFO [06-16|22:07:46.236] Last test factory exiting

Consensus error
Testcase: /fuzztmp/00000019-mixed-1.json
- gethbatch-0: /fuzztmp/gethbatch-0-output.jsonl
  - command: /gethvm statetest --trace --trace.format=json --trace.nomemory=true --trace.noreturndata=true
- eelsbatch-0: /fuzztmp/eelsbatch-0-output.jsonl
  - command: /ethereum-spec-evm statetest --json --noreturndata --nomemory
- nethbatch-0: /fuzztmp/nethbatch-0-output.jsonl
  - command: /neth/nethtest -x --trace -m
- besubatch-0: /fuzztmp/besubatch-0-output.jsonl
  - command: /evmtool/bin/evmtool --nomemory --notime --json state-test
- erigonbatch-0: /fuzztmp/erigonbatch-0-output.jsonl
  - command: /erigon_vm --json --noreturndata --nomemory statetest
- nimbusbatch-0: /fuzztmp/nimbusbatch-0-output.jsonl
  - command: /nimbvm --json --noreturndata --nomemory --nostorage
- evmone-0: /fuzztmp/evmone-0-output.jsonl
  - command: /evmone --trace /fuzztmp/00000019-mixed-1.json
- revm-0: /fuzztmp/revm-0-output.jsonl
  - command: /revme statetest --json /fuzztmp/00000019-mixed-1.json

```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/EpXWSoChQXyV1u1ozAH23w_

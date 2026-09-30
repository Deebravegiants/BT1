# [C] 5.1.4 Test failures inVMTests/vmPerformance/loopExp(potential issue inEXP)

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** zkevm-testvectors
**Description:** Some Ethereum tests fromVMTests/vmPerformance/loopExp.jsonare failing with the following
error:
Input: /0xPolygonHermez/zkevm-testvectors/tools/ethereum-tests/eth-inputs/GeneralStateTests/VMTests/looc
_↪_ → pExp_1.json
Start executor JS...
Error
Error: Program terminated with registers A, D, E, SR, CTX, PC, MAXMEM, zkPC not set to zero

The list of failing tests:

```
loopExp_
loopExp_
loopExp_
```

Tests can be found in our internal repository. They are modified versions of Ethereum tests with lowered transaction
gas limit and number of loop iterations decreased to fit into the 30M gas limit.
It is hard to diagnose the exact reason since testing infrastructure does not save trace log file (seeTrace log is not
saved in case of "register not set to zero" error) in case of such error (unlike in the case ofnewStateRoot does
not matcherror).
We think this may signal a bug in the implementation ofEXP.
**Recommendation:** Ensure these test can be executed and verify thatEXPbehaves correctly.
**Polygon-Hermez:** Fixed in PR #211 and improved zk-counters check in PR #

# [H] 5.1.12 Add_mirrorConnectorto_sendMessageofBaseMultichain

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BaseMultichain.sol#L39-L
**Description:** The function_sendMessage()ofBaseMultichainsends the message to the address of the_amb.
This doesn't seem right as the first parameter is the target contract to interact with according to multichain cross-
chain. This should probably be the_mirrorConnector.

```
function _sendMessage(address _amb, bytes memory _data) internal {
Multichain(_amb).anyCall(
_amb,// Same address on every chain, using AMB as it is immutable
...
);
}
```
**Recommendation:** Doublecheck the conclusion and change the code to:

- function _sendMessage(address _amb, bytes memory _data) ... {
+ function _sendMessage(address _amb, address _mirrorConnector, bytes memory _data) ... {
    Multichain(_amb).anyCall(
- _amb,
+ _mirrorConnector
    ...
    );
}

**Connext:** Solved in PR 2386.
**Spearbit:** Verified.

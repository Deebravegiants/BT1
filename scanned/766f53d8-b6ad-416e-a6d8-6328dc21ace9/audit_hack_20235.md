# [M] 5.2.4 Hardcode or whitelist the AxelardestinationAddress.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AxelarFacet.sol#L30-L
**Description:** The functionsexecuteCallViaAxelar()andexecuteCallWithTokenViaAxelar()call adestina-
tionAddresson thedestinationChain. ThisdestinationAddressneeds to have specific Axelar functions (_ex-
ecute()and_executeWithTokento()) be able to receive the calls. This is implemented in theExecutor. If these
functions don’t exist at thedestinationAddress, the transferred tokens will be lost.
/// @param destinationAddress the address of the LiFi contract on the destinationChain
function executeCallViaAxelar(..., string memory destinationAddress, ...) ... {
...
s.gateway.callContract(destinationChain, destinationAddress, payload);
}

Note: the comment "the address of the LiFi contract" isn’t clear, it could either be theLiFi Diamondor theExecu-
tor.
**Recommendation:** Hardcode or whitelist thedestinationAddress. Doublecheck the@paramcomment fordes-
tinationAddress(for both functions).
**LiFi:** We acknowledge the risk and recommend all users utilize our API in order to pass correct data and pass
invalid contract addresses at their own risk.
**Spearbit:** Acknowledged.

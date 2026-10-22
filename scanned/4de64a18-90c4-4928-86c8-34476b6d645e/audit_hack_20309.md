# [M] 5.2.17 Extra checks in_verifySender()ofGnosisBase.

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** GnosisBase.sol#L16-L19
**Description:** According to the Gnosis bridge documentation the source chain id should also be checked using
messageSourceChainId(). This is because in the future the same arbitrary message bridge contract could handle
requests from different chains.
If a malicious actor would be able to have access to the contract atmirrorConnectoron a to-be-supported chain
that is not theMIRROR_DOMAIN, they can send an arbitrary root to this mainnet/L1 hub connector which the con-
nector would mark it as coming from theMIRROR_DOMAIN. So the attacker can spoof/forge function calls and asset
transfers by creating a payload root and using this along with their access tomirrorConnectoron chain to send a
cross-chainprocessMessageto the Gnosis hub connector and after they can use their payload root and proofs to
forge/spoof transfers on the L1 chain.
Although it is unlikely that any other party could add a contract with the same address as_ambon another chain,
it is safer to add additional checks.
function _verifySender(address _amb, address _expected) internal view returns (bool) {
require(msg.sender == _amb, "!bridge");
return GnosisAmb(_amb).messageSender() == _expected;
}


**Recommendation:** In function_verifySender()add a check to verifymessageSourceChainId() == MIRROR_-
DOMAIN. Note: this will probably require adding an extra parameter to_verifySender().
**Connext:** ThechainId != domain, so has to be stored separately. Going to usesourceChainId()instead of the
messageSourceChainId()as there is no documentation of what thebytes32should represent instead ofuint256.
Solved in PR.
**Spearbit:** Verified.

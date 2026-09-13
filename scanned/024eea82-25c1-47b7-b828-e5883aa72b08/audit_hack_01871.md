# [H] Changing Verifier Address Doesn't Emit Event

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
In function `setVerifierAddress`, after the verifier address is changed, there is no event emitted, which means if the operator (security council) changes the verifier to a buggy verifier, or if the security council is compromised, the attacker can change the verifier to a malicious one, the unsuspecting user would still use the service, potentially lose funds due to the fraud transactions would be verified. 
#### Examples


**contracts/contracts/ZkEvmV2.sol:L83-L88**
```solidity
function setVerifierAddress(address _newVerifierAddress, uint256 _proofType) external onlyRole(DEFAULT_ADMIN_ROLE) {
  if (_newVerifierAddress == address(0)) {
    revert ZeroAddressNotAllowed();
  }
  verifiers[_proofType] = _newVerifierAddress;
}
```

<!--
Code URLs get formatted nicely, i.e. Vulnerable.sol#L27-L33
-->

#### Recommendation
Emits event after changing verifier address including old verifier address, new verifier address and the caller account

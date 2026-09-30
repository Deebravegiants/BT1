# [M] Tokens purchased via IssuanceController may be illegitimate

## Summary
Severity: Medium
Contest weight: 0.2194
Dataset id: 14337
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Within the set of contracts that implement the full functionality of the Havven system, balances for havven and nomin tokens are maintained in associated TokenState contracts. Havven and Nomin contracts interact with these TokenState contracts to, e.g., implement token transfers and modify user balances, while users interact with proxy contracts. This allows the owners to interchange the Havven and Nomin contracts in order to update the system’s functionality in the future.
The owner of IssuanceController can change the addresses of the Havven and Nomin contracts associated with the IssuanceController contract at any stage via the setHavven and setNomin functions. There are currently no checks to ensure that the new Havven and Nomin contracts refer to the associated TokenState contracts. A malicious owner could therefore substitute the Havven and Nomin contracts, such that eth could be collected via IssuanceController without actually issuing valid havven or nomin tokens (i.e., tokens that are registered by the underlying TokenState contracts).

## Recommendation
Checks could be implemented to provide users with some assurance that tokens purchased via IssuanceController are legitimate.
TokenState contracts have an associatedAddress, which refers to the address of the Nomin or Havven contract endowed with the power to modify balances in the TokenState.
IssuanceController could check that the addresses for the Nomin and Havven contracts associated with IssuanceController refer to the associatedAddress for the respective TokenState contracts.
Implementing this check would provide minor constraints on future topologies for the set of Havven contracts.
The check is also imperfect as a malicious owner could refer both the TokenState and IssuanceController contracts to a fraudulent address or arbitrarily modify the Nomin and Havven contracts. However, such activity would render the entire Havven system inactive, amplifying the consequences for malicious owner activity and thereby disincentivising bad behaviour.
Author’s Response
Implementing this check would have made future updates to the contracts more difficult for the Havven foundation to carry out. Since our contracts are already implemented behind proxies, allowing us to change them Havven Contract Review
at will, we did not believe the additional complexity yielded benefits to the community beyond the checks that are already in place. We have a vested interest in ensuring users only receive valid tokens when interacting with the issuance controller, and users can verify that tokens they receive are valid. We believe on a cost vs benefit analysis that this check wasn’t worth the additional complexity.
Havven Contract Review

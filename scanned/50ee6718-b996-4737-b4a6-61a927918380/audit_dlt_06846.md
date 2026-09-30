# [M] reputation risks with updateSolution

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-07-sherlock
Published: 2021-07-24
Source: https://github.com/code-423n4/2021-07-sherlock-findings/issues/4
Type: code-finding

## Details
# Handle

gpersoon


# Vulnerability details

## Impact
GovDev.sol has a function updateSolution to upgrade parts of the contract via the Diamond construction.
Via updateSolution any functionality can be changed and all the funds can be accessed/rugged.
Even if this is well intended the project could still be called out resulting in a reputation risk, see for example:
https://twitter.com/RugDocIO/status/1411732108029181960

Note: there is a function transferGovDev which can be used to disable the updateSolution

## Proof of Concept
// https://github.com/code-423n4/2021-07-sherlock/blob/main/contracts/facets/GovDev.sol#L25
  function updateSolution(IDiamondCut.FacetCut[] memory _diamondCut,address _init,bytes memory _calldata) external override {
    require(msg.sender == LibDiamond.contractOwner(), 'NOT_DEV');
    return LibDiamond.diamondCut(_diamondCut, _init, _calldata);
  }
}
## Tools Used

## Recommended Mitigation Steps
Apply extra safeguards for example to limit the time period where updateSolution can be used.

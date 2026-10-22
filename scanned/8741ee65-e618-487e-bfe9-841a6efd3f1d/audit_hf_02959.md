# [C] Anyone can change the base URI

## Summary
Severity: Critical
Contest weight: 0.2297
Dataset id: 16392
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a collection is deployed through WizardLaunchpad::deployCollection, an ipfsHash parameter is passed by the user to set the _baseuri. However, the setbaseUri function in ERC721ForCollection is a public function and can be called by anyone. This means that anyone can change the base URI.
```solidity
function setbaseUri(string memory uri) public {
    _baseuri = uri;
}
```

## Recommendation
Add an appropriate access control modifier.

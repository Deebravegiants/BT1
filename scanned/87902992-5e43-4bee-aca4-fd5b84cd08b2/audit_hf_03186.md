# [M] registerTemplate() can't handle properly when

## Summary
Severity: Medium
Contest weight: 0.5609
Dataset id: 17759
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Factory.sol when register one template, and template's version is 0, the latestImplementation[templateName] will be address(0) and add other version, "_templateNames" will duplicate. When version is equal 0 latestImplementation[templateName] don't set.
```solidity
function _setTemplate(
    string memory templateName,
    uint256 templateVersion,
    address implementationAddress
) internal {
    ...
    if (latestImplementation[templateName] == address(0)) { /****add other version, _templateNames will duplicate ****/
        _templateNames.push(templateName);
    }
    if (templateVersion > latestVersion[templateName]) {
        latestVersion[templateName] = templateVersion;
        latestImplementation[templateName] = implementationAddress;
        /****templateVersion==0 , don't set ****/
    }
}
```
latestImplementation[templateName] and _templateNames will error. external contracts may think there is no setup, resulting in duplicate setups that keep failing

## Recommendation
```solidity
function _setTemplate(
    string memory templateName,
    uint256 templateVersion,
    address implementationAddress
) internal {
    if (templateVersion >= latestVersion[templateName]) {
        latestVersion[templateName] = templateVersion;
        latestImplementation[templateName] = implementationAddress;
    }
}
```

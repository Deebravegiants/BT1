# [M] Loss of Veto Power can Lead to 51% Attack

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-09-nouns-builder
Published: 2022-09-15
Source: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/533
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L76
https://github.com/code-423n4/2022-09-nouns-builder/blob/7e9fddbbacdd7d7812e912a369cfd862ee67dc03/src/governance/governor/Governor.sol#L596-L602


# Vulnerability details

## Impact
The veto power is import functionality for current Nouns DAO logic in order to protect their treasury from malicious proposals. 
However there is lack of zero address check and lack of 2 step address changing process for vetoer address.
This might lead to DAO owner losing their veto power unintentionally and open to 51% attack which can drain their entire treasury.

https://dialectic.ch/editorial/nouns-governance-attack
https://dialectic.ch/editorial/nouns-governance-attack-2

## Proof of Concept
Lack of 0-address check for vetoer address at initialize() of Governor.sol
Also I recommend to make changing address process of vetoer at updateVetoer() into 2-step process to avoid accidently setting
vetoer to arbitrary address and end up lossing veto power unintentionally.
```
Governor.sol:
57:    function initialize(
         ...
76:        settings.vetoer = _vetoer;
```
```
596:    function updateVetoer(address _newVetoer) external onlyOwner {
597:        if (_newVetoer == address(0)) revert ADDRESS_ZERO();
599:        emit VetoerUpdated(settings.vetoer, _newVetoer);
601:        settings.vetoer = _newVetoer;
602:    }
```

## Tools Used
Manual Analysis

## Recommended Mitigation Steps

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-09-nouns-builder-findings/issues/533_

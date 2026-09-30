# [M] UUPSUpgradeable vulnerability in OpenZep-

## Summary
Severity: Medium
Contest weight: 0.1228
Dataset id: 20322
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Openzeppelin has found the critical severity bug in UUPSUpgradeable. The kyber-swap contracts has used both openzeppelin contracts as well as openzeppelin upgrabable contracts with version v4.3.1. This is confirmed from package.json.
File: ks-elastic-sc/package.json
"@openzeppelin/contracts": "4.3.1",
"@openzeppelin/test-helpers": "0.5.6",
"@openzeppelin/contracts-upgradeable": "4.3.1",
The UUPSUpgradeable vulnerability has been found in openzeppelin version as follows,
Openzeppelin bug acceptance and fix: check here
The following contracts has been affected due to this vulnerability
1) PoolOracle.sol
2) TokenPositionDescriptor.sol
Upgradeable contracts using UUPSUpgradeable may be vulnerable to an attack affecting uninitialized implementation contracts.

## Recommendation
1) Update the openzeppelin library to latest version.
2) Check this openzeppelin security advisory to initialize the UUPS implementation contracts.
3) Check this openzeppelin UUPS documentation.

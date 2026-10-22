# [H] OZ ERC1155Supply vulnerability

## Summary
Severity: High
Contest weight: 0.1678
Dataset id: 1170
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Overlay uses OZ contracts version 4.3.2:

  dependencies:
    - OpenZeppelin/openzeppelin-contracts@4.3.2

and has a contract that inherits from ERC1155Supply:

  contract OverlayV1OVLCollateral is ERC1155Supply

This version has a recently discovered vulnerability: <https://github.com/OpenZeppelin/openzeppelin-contracts/security/advisories/GHSA-wmpv-c2jp-j2xg>

In your case, function unwind relies on totalSupply when calculating `_userNotional`, `_userDebt`, `_userCost`, and `_userOi`, so a malicious actor can exploit this vulnerability by first calling ‘build’ and then on callback ‘unwind’ in the same transaction before the total supply is updated.

## Recommendation
Consider updating to a patched version of 4.3.3.

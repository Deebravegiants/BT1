# [H] Unable to compile contracts

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

In the `Fairswap_iDOLvsImmortalOptions`repository: 

Compilation with truffle fails due to a missing file: `contracts/testTokens/TestBondMaker.sol`. 
Compilation with `solc` fails due to an undefined interface function:

```
Error: Member "calculatePrice" not found or not visible after argument-dependent lookup in contract CalculatorInterface.
   --> contracts/BoxExchange.sol:821:36:
    |
821 |         uint256[5] memory Prices = calc.calculatePrice(
    |                                    ^^^^^^^^^^^^^^^^^^^
```

In the `Fairswap_iDOLvsLien` repository: 

Compilation with truffle fails due to a missing file: `./ERC20RegularlyRecord.sol`. The correct filename is `./TestERC20RegularlyRecord.sol`. 

#### Recommendation

Ensure all contracts are easily compilable by following simple instructions in the README.

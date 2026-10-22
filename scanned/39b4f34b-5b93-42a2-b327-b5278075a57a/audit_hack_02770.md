# [M] Hard coding of EULER address may become unusable in possible update

## Summary
Severity: Medium
Reporter: 0xSmartContract
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L26-L28
Type: audit-issue

## Details
# Hard coding of EULER address may become unusable in possible update

## Summary
In the "EulerStrategy.sol" contract, the EULER address is hard coded and cannot be changed. This code pattern is similar to other Strategy conventions.
However, currently the "low-level call optimizer bug" is a very new vulnerability and it is possible that the EULER proxy contract may be affected, so it would be correct to encode the EULER address in an updatable way rather than hard-coding it.




## Vulnerability Detail

[EulerStrategy.sol#L26-L28](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L26-L28)
```js
  // https://docs.euler.finance/protocol/addresses
  address public constant EULER = 0x27182842E098f60e3D576794A5bFFb0777E025d3;
  // https://github.com/euler-xyz/euler-contracts/blob/master/contracts/modules/EToken.sol
  IEulerEToken public constant EUSDC = IEulerEToken(0xEb91861f8A4e1C12333F42DCE8fB0Ecdc28dA716);

```




## Impact

The subject audit will not go into detail as it does not cover the EULER proxy contract.

Certora, discovered a previously unknown optimization bug in the Solidity compiler (version 8.14 and lower). This bug causes the optimizer to consider some memory operations in inline assembly as being "dead" and remove them. Later operations that would read the values written by these improperly removed memory operations will instead observe the old version of memory.

EULER proxy contract:
https://etherscan.io/address/0x27182842E098f60e3D576794A5bFFb0777E025d3#code#F1#L49

```js
 assembly {
            let payloadSize := sub(calldatasize(), 4)
            calldatacopy(0, 4, payloadSize)
            mstore(payloadSize, shl(96, caller()))
            let result := delegatecall(gas(), moduleImpl, 0, add(payloadSize, 20), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
                case 0 { revert(0, returndatasize()) }
                default { return(0, returndatasize()) }
        }
```

Bug Details:
https://blog.soliditylang.org/2022/09/08/storage-write-removal-before-conditional-termination/

https://github.com/ethereum/solidity-blog/blob/499ab8abc19391be7b7b34f88953a067029a5b45/_posts/2022-06-15-inline-assembly-memory-side-effects-bug.md


## Code Snippet
[EulerStrategy.sol#L26-L28](https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L26-L28)

## Tool used

Manual Review

## Recommendation
Add a function that will make the EULER address changeable - updatable independently of other projects

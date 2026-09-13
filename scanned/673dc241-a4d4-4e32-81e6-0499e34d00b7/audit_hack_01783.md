# [M] Re-entrancy risk in UniERC20

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
UniERC20 is a general library for facilitating transfers of any ERC20 or native coin assets. It features gas-efficient code and could be easily integrated into large systems of contract, such as those that are used in this audit -- 1inch routers and limit order protocol.

However, it also utilizes `.call(){value:X}` method of transferring chain native assets, such as ETH. This introduces a large risk in the form of re-entrancy attacks, so any system implementing this library would have to handle them. While 1inch's projects in the scope of this audit do not seem to have re-entrancy attack vectors, other projects that could be utilizing this library might. Since this is an especially efficient and convenient library, the likelihood that some other project using this suffers and then sufferring a re-entrancy attack is significant.

**solidity-utils/contracts/libraries/UniERC20.sol:L45**
```solidity
(bool success, ) = to.call{value: amount}("");  // solhint-disable-line avoid-low-level-calls
```

**solidity-utils/contracts/libraries/UniERC20.sol:L62**
```solidity
(bool success, ) = to.call{value: msg.value - amount}("");  // solhint-disable-line avoid-low-level-calls
```

Consider instead implementing `transfer()` or `send()` methods for transferring chain native assets, such as ETH, instead of performing a `.call()`

# [M] `transferSAFEOwnership`

## Summary
Severity: Medium
Contest weight: 0.6562
Dataset id: 19438
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Function `transferSAFEOwnership()` is only callable by `Only Vault721`: `require(msg.sender == address(vault721), 'SafeMngr: Only Vault721');` and its purpose is to give the safe ownership to a `dst` address. However, `transferSAFEOwnership()` does not reset `safeCan` mapping which is used by `safeAllowed` modifier.

This leads to some security issues. The modifier `safeAllowed` is used to verify if user has permission to the safe. Multiple of functions which perform critical operations on the safe use this modifier to verify is user has permission to call that operation on a given safe.

Since `transferSAFEOwnership()` transfer ownership to a different address, it should also reset all previously set privileges by the previous owner. However, `safeCan` mapping is not being reset in `transferSAFEOwnership()`

## Proof of Concept
Firstly, let’s take a look how `safeAllowed` modifier is defined:

[File: ODSafeManager.sol](https://github.com/open-dollar/od-contracts/blob/f4f0246bb26277249c1d5afe6201d4d9096e52e6/src/contracts/proxies/ODSafeManager.sol#L49-L53)

```solidity
modifier safeAllowed(uint256 _safe) {
  address _owner = _safeData[_safe].owner;
  if (msg.sender != _owner && safeCan[_owner][_safe][msg.sender] == 0) revert SafeNotAllowed();
  _;
}
```

For this PoC, let’s consider user `A`, who’s the owner of safe 123.  
He gives access to the safe to `X`, `Y`, so he calls:  
`allowSAFE(123, X, 1), allowSAFE(123, Y, 1)`;

[File: ODSafeManager.sol](https://github.com/open-dollar/od-contracts/blob/f4f0246bb26277249c1d5afe6201d4d9096e52e6/src/contracts/proxies/ODSafeManager.sol#L49-L53)

```solidity
function allowSAFE(uint256 _safe, address _usr, uint256 _ok) external safeAllowed(_safe) {
  address _owner = _safeData[_safe].owner;
  safeCan[_owner][_safe][_usr] = _ok;
  emit AllowSAFE(msg.sender, _safe, _usr, _ok);
}
```

After calling this function, `safeCan` mapping looks like this: `safeCan[A][123][X] = 1` and `safeCan[A][123][Y] = 1`.

Now, there’s a call to transfer safe ownership to `_dst` B: `transferSAFEOwnership(123, B)`.

[File: ODSafeManager.sol](https://github.com/open-dollar/od-contracts/blob/f4f0246bb26277249c1d5afe6201d4d9096e52e6/src/contracts/proxies/ODSafeManager.sol#L49-L53)

```solidity
function transferSAFEOwnership(uint256 _safe, address _dst) external {
  require(msg.sender == address(vault721), 'SafeMngr: Only Vault721');

  if (_dst == address(0)) revert ZeroAddress();
  SAFEData memory _sData = _safeData[_safe];
  if (_dst == _sData.owner) revert AlreadySafeOwner();

  _usrSafes[_sData.owner].remove(_safe);
  _usrSafesPerCollat[_sData.owner][_sData.collateralType].remove(_safe);

  _usrSafes[_dst].add(_safe);
  _usrSafesPerCollat[_dst][_sData.collateralType].add(_safe);

  _safeData[_safe].owner = _dst;

  emit TransferSAFEOwnership(msg.sender, _safe, _dst);
}
```

It modifies only `_usrSafes`, `_usrSafesPerCollat` and `_safeData` mappings and does not modify `safeCan` mapping. After `transferSAFEOwnership(123, B)` call, those mappings look like this:

```
_usrSafes[B] = [123]
_usrSafesPerCollat[B][_sData.collateralType] = [123]
_safeData[123].owner = B;

safeCan[A][123][X]  // notice this is from previous allowSAFE() call
safeCan[A][123][Y]  // notice this is from previous allowSAFE() call
```

Now, at some point in the future, the safe goes back to user A. Function `transferSAFEOwnership()` is being called once again: `transferSAFEOwnership(123, A)`.

User `A` get access to the safe. However, he does not remember that he previously sets access to users `X` and `Y`. Those mappings:

```
safeCan[A][123][X]
safeCan[A][123][Y]
```

are still there - meaning that `X` and `Y` has still access to that safe, even though the safe was just transferred back to `A` and safe’s permissions should be cleared.

Now, when user `X` or `Y` will try to call any function with `safeAllowed` modifier - they will be allowed, since `safeAllowed` will return true for them, because `X` and `Y` are still in `safeCan` mapping.

## Recommendation
Whenever transfer ownership - make sure to reset `safeCan[old_owner][safe]` mapping.

The warden has demonstrated how `transferSAFEOwnership()` does not clear safe permissions in `safeCan`, which will cause previously “approved” addresses to still have access under the following conditions:

  * An owner regains ownership of the safe after transferring it away. 
  * The previously “approved” address becomes malicious.
  * The owner does not call `allowSAFE()` beforehand to remove the “approved” address.

This is unintended functionality, but given that it requires multiple unlikely conditions for this to become a problem, I believe medium severity is appropriate.

# [H] 6.1 EIP-170 Mix Up / Unlimited Contract Size

## Summary
Severity: High
Source: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-170.md
Type: audit-issue

## Details
Correctness High Version 1 Risk Accepted

EIP-170 has been introduced into the Ethereum mainnet with the Spurious Dragon hardfork in order to
limit the maximum codesize of a contract.

The short specification of the EIP reads:

```
... if contract creation initialization returns data with length of more than 0x6000 (2**14 + 2**13) bytes,
contract creation fails with an out of gas error.
```
The data returned by the contract creation initialization is the code of the newly deployed smart contract
that will be stored as the code of the smart contract. This is valid regardless wether the contract has been
deployed directly from a transaction or a during code execution of a CREATE / CREATE2 opcode. For
more details please refer to chapter 7 of the Ethereum Yellowpaper.

The TxPermissionBased contract in the POSDAO system attempts to enforce a
_deployerInputLengthLimit. There is an annotated function for the owner to set this variable:

```
/// @dev Sets the limit of `input` transaction field length in bytes
/// for contract deployment transaction made by the specified deployer.
/// @param _deployer The address of a contract deployer.
```

```
/// @param _limit The maximum number of bytes in `input` field of deployment transaction.
/// Set it to zero to reset to default 24Kb limit defined by EIP 170.
```
And inside the _allowedTxTypes function which is annotated with:

```
/// @dev Defines the allowed transaction types which may be initiated by the specified sender with
/// the specified gas price and data. Used by node's engine each time a transaction is about to be
/// included into a block.
```
there is:

```
if (_to == address(0) && _data.length > deployerInputLengthLimit(_sender)) {
// Don't let to deploy too big contracts
return (NONE, false);
}
```
There is a mixup here: What the TxPermission contract actually limits with this parameter is the lenght
of the data field of the transaction, not the limit of a contract's code size. This has nothing to do with
EIP-170. Hence if the limit is only "enforced" by the TxPermission contract and there is no further limit
set in the chain specification anyone may deploy a contract of arbitrary size, limited only by the gas limit.
EIP-170 is not activated in the template/spec.json chain sepcification file available in the repository.

Note that the Ethereum mainnet has no excplicit limit on the data field of a transaction (called input in the
function description in POSDAO). This is only limited by the gas limit of a block.

Ethereum Yellowpaper: https://ethereum.github.io/yellowpaper/paper.pdf
EIP-170 Specification: https://github.com/ethereum/EIPs/blob/master/EIPS/eip-170.md

Risk Accepted:

POA Network accepts this risk and states: Some popular projects on xDai require the abi
lity to deploy contracts with size greater than 24 Kb. The limit on transacti
on size is intended as an easy protection against script kiddies.

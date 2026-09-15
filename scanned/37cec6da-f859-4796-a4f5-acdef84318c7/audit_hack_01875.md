# [H] Missing Public Inputs Range Check

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description
The public input is an array of `uint256` numbers, there is no check if each public input is less than SNARK scalar field  modulus `r_mod`, as mentioned in the step 3 of the verifier's algorithm in the [Plonk paper](https://eprint.iacr.org/2019/953.pdf). Since public inputs are involved computation of `Pi` in the plonk gate which is in the SNARK scalar field, without the check, it might cause scalar field overflow and the verification contract would fail and revert. To prevent overflow and other unintended behavior there should be a range check for the public inputs.  
#### Examples

**contracts/Verifier.sol:L470**
```solidity
function Verify(bytes memory proof, uint256[] memory public_inputs) 
```


**contracts/Verifier.sol:L367-L383**
```solidity
sum_pi_wo_api_commit(add(public_inputs,0x20), mload(public_inputs), zeta)
pi := mload(mload(0x40))

function sum_pi_wo_api_commit(ins, n, z) {
  let li := mload(0x40)
  batch_compute_lagranges_at_z(z, n, li)
  let res := 0
  let tmp := 0
  for {let i:=0} lt(i,n) {i:=add(i,1)}
  {
    tmp := mulmod(mload(li), mload(ins), r_mod)
    res := addmod(res, tmp, r_mod)
    li := add(li, 0x20)
    ins := add(ins, 0x20)
  }
  mstore(mload(0x40), res)
}
```


#### Recommendation
Add range check for the public inputs
`require(input[i] < r_mod, "public inputs greater than snark scalar field");`

<!-- Supply advice on how to best fix the problem. -->

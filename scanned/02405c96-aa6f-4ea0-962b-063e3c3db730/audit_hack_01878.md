# [M] Wrong ID for `OutsideExecution` Interface

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

While not standardized across the community, the Argent team has decided to isolate the "outside execution" functionality in a separate interface, so other teams in the ecosystem can choose to implement that interface as well.


**contracts/lib/src/outside_execution.cairo:L10-L29**
```solidity
/// Interface ID: 0x3a8eb057036a72671e68e4bad061bbf5740d19351298b5e2960d72d76d34cb9
// get_outside_execution_message_hash is not part of the standard interface
#[starknet::interface]
trait IOutsideExecution<TContractState> {
    /// @notice This method allows anyone to submit a transaction on behalf of the account as long as they have the relevant signatures
    /// @param outside_execution The parameters of the transaction to execute
    /// @param signature A valid signature on the Eip712 message encoding of `outside_execution`
    /// @notice This method allows reentrancy. A call to `__execute__` or `execute_from_outside` can trigger another nested transaction to `execute_from_outside`.
    fn execute_from_outside(
        ref self: TContractState, outside_execution: OutsideExecution, signature: Array<felt252>
    ) -> Array<Span<felt252>>;

    /// Get the status of a given nonce, true if the nonce is available to use
    fn is_valid_outside_execution_nonce(self: @TContractState, nonce: felt252) -> bool;

    /// Get the message hash for some `OutsideExecution` following Eip712. Can be used to know what needs to be signed
    fn get_outside_execution_message_hash(
        self: @TContractState, outside_execution: OutsideExecution
    ) -> felt252;
}
```

SNIP-5 – as already mentioned in 6 – is a StarkNet Improvement Proposal that describes how to publish and detect what interfaces a contract implements. To briefly summarize, the interface ID is defined as the XOR of the extended selectors of the functions in the interface, and a function's extended selector is the `starknet_keccak` hash of the function signature, where some special rules define how to deal with the different data types. Deriving the input for `starknet_keccak` can be done manually, but it is tedious, error-prone, and can even be somewhat involved, as it may require knowledge of some Cairo internals, depending on the types used in the function.

When we tried to verify the ID for the `OutsideExecution` interface, we noticed a mismatch between the result of our own calculations and the ID the Argent team had arrived at:


**contracts/lib/src/outside_execution.cairo:L7-L8**
```solidity
const ERC165_OUTSIDE_EXECUTION_INTERFACE_ID: felt252 =
    0x3a8eb057036a72671e68e4bad061bbf5740d19351298b5e2960d72d76d34cb9;
```

Together with the client, we were able to identify a mistake that was made in the manual derivation of the input to the hash function, leading to a wrong extended function selector and, therefore, an incorrect interface identifier.

 The correct extended function selector for `execute_from_outside` is:
```
starknet_keccak(
    'execute_from_outside(
        (ContractAddress,felt252,u64,u64,(@Array<(ContractAddress,felt252,Array<felt252>)>)),
        Array<felt252>
     )->Array<(@Array<felt252>)>'
) = 0x3c6e798a947887809ab7c506818dac2e3632acafa20cb51d2fff56b3577dc75
```
(The line breaks were only inserted for better readability in this document. The string does not contain any whitespace.)

#### Recommendation

Together with the extended function selector for `is_valid_outside_execution_nonce`,  `0x3ae284922d559e87220df9c5a51dae59c391ce8f3b4fabb572275e210299df4`, the resulting interface ID for `OutsideExecution` is `0x68cfd18b92d1907b8ba3cc324900277f5a3622099431ea85dd8089255e4181`, and the definition of `ERC165_OUTSIDE_EXECUTION_INTERFACE_ID` should be changed accordingly.

Note that the Argent team has deliberately omitted `get_outside_execution_message_hash` from the interface (in the sense of SNIP-5).

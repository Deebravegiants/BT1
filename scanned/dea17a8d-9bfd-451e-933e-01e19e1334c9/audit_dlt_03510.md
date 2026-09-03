# [M] handle_l1_message may unfairly revert l2 tx with sufficient l1 sender balance, due to vulnerable fee charge implementation

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-09-kakarot
Published: 2024-10-24
Source: https://github.com/code-423n4/2024-09-kakarot-findings/issues/29
Type: code-finding

## Details
# Lines of code

https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L950
https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L1032


# Vulnerability details

## Proof of Concept
`handle_l1_message` can only be invoked by starknet os(`@l1_handler`) and is not a regular user invoked transaction from `eth_send_raw_unsigned_tx` flow. (kakarot::[handle_l1_message](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/kakarot.cairo#L370) -> library:[handle_l1_message](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/library.cairo#L421) -> Interpreter::[execute](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L820))

`handle_l1_message` [hardcodes EVM gaslimit(2100000000) and gasprice(1)](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/library.cairo#L436) for every L1->L2 message regardless of the complexity of the actual l2 tx. In interpreter::execute, L1sender's cached balance will be subtracted with the [max_fee (2100000000 x 1)](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L950-L951) first before performing ETH transfer or running EVM.

Case: L1 sender performs minimal operations on L2
For an L1 sender who only transfers some ETH to a L2 address or perform simple opcodes, the actual gas cost (`required_gas`) may be very close to the [intrinsic gas cost(21000)](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L847). This means the `actual_fee` l1sender is required to pay is around 21000 x 1, which is far less than the calculated `max_fee` 2100000000 x 1.

In this case, interpreter::execute will first subtract `max_fee`(2100000000) from L1sender's cached balance(`Account.set_balance(sender, &new_balance)`). Note that this cached balance subtraction is done before ETH value transfer and `run(evm)`, which means any subsequent logic will be using L1sender's new_balance (e.g. X - 2100000000). 
```rust
//src/kakarot/interpreter.cairo
    func execute{
...
    }(
        env: model.Environment*,
        address: model.Address*,
        is_deploy_tx: felt,
        bytecode_len: felt,
        bytecode: felt*,
        calldata_len: felt,
        calldata: felt*,
        value: Uint256*,
        gas_limit: felt,
        access_list_len: felt,
        access_list: felt*,
    ) -> (model.EVM*, model.Stack*, model.Memory*, model.State*, felt, felt) {
...
|>      let max_fee = gas_limit * env.gas_price;
        let (fee_high, fee_low) = split_felt(max_fee);
        let max_fee_u256 = Uint256(low=fee_low, high=fee_high);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-09-kakarot-findings/issues/29_

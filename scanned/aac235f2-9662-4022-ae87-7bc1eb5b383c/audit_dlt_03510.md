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

        with state {
            let sender = State.get_account(env.origin);
            //@audit L1->L2 flow: L1 sender's cached is first subtracted with max_fee based on hardcoded values, regardless of the actual fee required based on L2tx's complexity
|>          let (local new_balance) = uint256_sub([sender.balance], max_fee_u256);
            let sender = Account.set_balance(sender, &new_balance);
...
            let transfer = model.Transfer(sender.address, address, [value]);
            let success = State.add_transfer(transfer);
...
        if (success == 0) {
            let (revert_reason_len, revert_reason) = Errors.balanceError();
            tempvar evm = EVM.stop(evm, revert_reason_len, revert_reason, Errors.EXCEPTIONAL_HALT);
        } else {
            tempvar evm = evm;
        }

        with stack, memory, state {
            let evm = run(evm);
        }

        let required_gas = gas_limit - evm.gas_left;
...
        let actual_fee = total_gas_used * env.gas_price;
        let (fee_high, fee_low) = split_felt(actual_fee);
        let actual_fee_u256 = Uint256(low=fee_low, high=fee_high);
        let transfer = model.Transfer(sender.address, coinbase.address, actual_fee_u256);

        with state {
            State.add_transfer(transfer);
            State.finalize();
        }

        return (evm, stack, memory, state, total_gas_used, required_gas);
```
(https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L950-L951)

POC: 
Suppose L1sender's current balance is (2100000000 + 21000). And L1sender wants to transfer 2100000000 to an L2 address. Suppose the `required_gas` is only 21000 so that L1sender's current balance is sufficient.
1. In interpreter::execute, `max_fee`(2100000000) is first subtracted from L1sender's cached balance. new_balance = 2100
2. ETH `value`(2100000000) transfer logic is performed based on the cached new balance. (`let success = State.add_transfer(transfer)`) Because in the cached state 2100 - 2100000000 < 0, success -> 0.
3. `success == 0` logic is executed, EVM tx reverts with an [EXCEPTIONAL_HALT](https://github.com/kkrt-labs/kakarot/blob/7411a5520e8a00be6f5243a50c160e66ad285563/src/kakarot/interpreter.cairo#L985).
4. Due to evm reverted with exceptional halt, total gas is consumed, max fee 2100000000 is charged. 

The above shows that despite L1sender having enough balance to perform the L2 tx, L1sender's tx is reverted with max fee 2100000000 charged. L1sender only has 21000 left after the tx and no transfer is done. 

Impacts: L1sender's L2 tx can be unfairly reverted when they have enough balance to cover transfer value and the actual fee. 

Because `handle_l1_message` is not invoked by rpc endpoint users, L1 sender doesn't have a chance to specify `max_fee` value. In such cases, L1 sender might only reasonably expect to have the EVM gas cost sufficient based on the complexity of the L2 tx, which can be much lower than `max_fee`. Although max_fee is marginal in ETH value, L1 sender's L2 tx can still fail due to the sequence of fee deduction in the cached state. The failure is not the L1 sender's fault.
 
## Recommended Mitigation Steps
Because `handle_l1_message` is different from `eth_send_raw_unsigned_tx` in its invocation and max_fee setting. Consider allowing L1sender to input `gas_limit` from L1, and decode the user input `gas_limit` in handle_l1_message to compute max_fee. Or refactor the control flow to skip max fee deduction when called from handle_l1_message.






## Assessed type

Other

# [C] Receiver May Spend Minted Funds Before Peg-In Proof Is Verified

## Summary
Severity: Critical
Contest weight: 0.6411
Dataset id: 15132
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Receiver funds cannot be retracted for an invalid proof when they have already been spent.
In mint() the receiver is called with the minted amount on line 80. During this call the receiver may perform arbitrary calls, including spending the balance that they just received. If the peg-in proof is later deemed invalid the protocol attempts to decrement the receivers balance. However, seeing as that balance was already spent, a panic occurs. As such, an attacker can crash every node on the network at the same time by spending the received balance during this call.
The funds are distributed during the call to mint() as seen in the following code snippet.
Minting.sol
```solidity
function mint(
address destination,
uint256 amount,
uint32 bitcoinBlockHeight,
bytes calldata metadata,
address refundAddress
) public {
    (bool successMint, ) = payable(destination).call{value: amount}(""); //@audit receiver gains control of execution flow here
    require(successMint, "Mint to destination failed");
}
```
After a mint() transaction is complete, the core node’s state transition will extract Mint events and verify the proof and decrement the user balance if the proof is invalid. The balance decrementing panics due to the expect() on an overflow.
crates/ethereum/evm/src/execute.rs
```rust
fn decrement_balance_by_address(address: Address, amount: EthersU256, state: &mut EvmState) {
    let mut account = state.get(&address).expect("Account to exist").clone();
    // print balance before decrement
    info!("Balance before decrement: {:?}", account.info.balance);
    // decrement balance by amount
    info!("Decrementing address: {:?} by {:?}", address, amount);
    account.info.balance = account
        .info
        .balance
        .checked_sub(U256::from_be_bytes(amount.into()))
        .expect("No overflow for checked_sub");
    // update state with new balance
    state.insert(address, account);
}
```
The impact and likelihood is rated as high as any user may create a transaction which calls the mint() function to crash the nodes and stall the network.
Macbeth Review

## Recommendation
A solution is to modify the Minting.sol contract such that the receiver and refundAddress are not immediately minted funds. Instead increment the receivers balance directly during the core node state transition function after verifying the peg-in proof.
The solution is similar to the one proposed in BTNX-06.

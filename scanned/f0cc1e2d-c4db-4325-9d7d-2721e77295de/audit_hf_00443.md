# [H] There is no mechanism in the EVM bridge to cover gas fees

## Summary
Severity: High
Contest weight: 0.6340
Dataset id: 1865
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is a mechanism for covering gas fees in the Solana Bridge, but none exists in the EVM Bridge, leading to potential fund losses for the protocol. As you can see in the burn() function of the Solana Bridge program, certain fees are incurred.
```rust
pub fn burn(
    ctx: Context<Burn>,
    name: String,
    amount: u64,
    fee: u64,
    target_network: u8,
    target_address: String,
) -> Result<()> {
    emit!(EventBurn {
        from: *ctx.accounts.signer.to_account_info().key,
        mint: *ctx.accounts.mint.to_account_info().key,
        name: name.clone(),
        amount,
        fee,
        target_network,
        target_address,
    });
    if fee > 0 {
        anchor_lang::system_program::transfer(
            CpiContext::new(
                ctx.accounts.system_program.to_account_info(),
                anchor_lang::system_program::Transfer {
                    from: ctx.accounts.signer.to_account_info(),
                    to: ctx.accounts.bridge_signer.to_account_info(),
                },
            ),
            fee,
        )?;
    }
    [... ...]
}
```
This fee covers the gas cost when the protocol initiates a transaction to mint the corresponding tokens on the target network and should not be less than 50,000,000 lamports (0.05 SOL, approximately $10).
https://github.com/runemine/bridge/tree/76ca43cb0a519c81b0045efede9b8e584152e4da/bridge/bridge/chain_sol.go#L72-L74
```go
if fee < 50000000 {
    panic(fmt.Sprintf("sol fee paid to small to cover transaction cost: %d", fee))
}
```
In contrast, when locking or burning tokens in the EVM Bridge, users do not incur any additional fees. As a result, when users bridge tokens from EVM to Solana, the protocol must cover the transaction fees required to initiate the transactions for minting or unlocking tokens on Solana.
https://github.com/runemine/bridge/tree/76ca43cb0a519c81b0045efede9b8e584152e4da/bridge/contract-evm/Bridge.sol#L104-L124
```solidity
function burn(
    string calldata name,
    uint16 targetNetwork,
    string calldata to,
    uint256 amount
) external {
    address token = tokens[name];
    Token(token).burn(msg.sender, amount);
    emit Burn(token, msg.sender, name, targetNetwork, to, amount);
}

// transfer in a token which is native to this chain, emitting an event the bridge will notice
function lock(
    address token,
    uint16 targetNetwork,
    string calldata to,
    uint256 amount
) external {
    Token(token).transferFrom(msg.sender, address(this), amount);
    emit Lock(token, msg.sender, targetNetwork, to, amount);
}
```
This vulnerability can be exploited by attackers, potentially leading to significant financial losses for the protocol through repeated minimal burns or locks.
Internal pre-conditions
none
External pre-conditions
none
Attack Path
Let's consider the following scenario:
1. Alice, the attacker, selects a target chain with the highest transaction fees for minting or unlocking tokens.
2. Alice repeatedly burns or locks dust amounts in the EVM Bridge.
As a result, Alice's burns and locks will trigger the protocol to initiate transactions to mint or unlock the corresponding tokens on the target chain, leading to significant transaction fees incurred by the protocol.
Loss of funds for the protocol.

## Recommendation
No recommendation available

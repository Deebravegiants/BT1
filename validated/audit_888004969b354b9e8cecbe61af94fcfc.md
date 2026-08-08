### Title
Balance-only "already in use" check in System Program `CreateAccount` enables pre-funding griefing/DoS - (File: `programs/system/src/system_processor.rs`)

### Summary
The Sherlock report describes `_existsPairPool()` inferring the existence/state of an on-chain entity purely from `ERC20.balanceOf()`, which any unprivileged actor can manipulate by sending tokens to an address, causing downstream operations to revert. Agave's System Program contains a structurally identical pattern in its `create_account` instruction handler: it infers whether an account is "already in use" purely from its lamport balance, without checking owner or data, allowing any unprivileged user to grief legitimate account-creation transactions by pre-funding the destination address.

### Finding Description
`create_account()` in `programs/system/src/system_processor.rs` decides whether the destination account can be created solely by checking if it currently holds any lamports: [1](#0-0) 

```rust
{
    let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
    if to.get_lamports() > 0 {
        ic_msg!(
            invoke_context,
            "Create Account: account {:?} already in use",
            to_address
        );
        return Err(SystemError::AccountAlreadyInUse.into());
    }
    allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
}
```

This mirrors the root cause pattern in the report: existence/usability of an account is inferred from a balance signal (`lamports > 0`) rather than verifying the account's real state (owner, data, or whether it was actually created by the expected program). Any unprivileged party can transfer a trivial amount of lamports (e.g., via `SystemInstruction::Transfer`) to a deterministically computable destination address — a PDA, an associated token account, a nonce account address, a stake account address, etc. — *before* the legitimate `CreateAccount` transaction lands. Because the check only looks at `lamports > 0` and does not validate ownership or data length, the legitimate creation attempt fails with `AccountAlreadyInUse`, exactly analogous to how the Dodo contracts falsely conclude a "pool exists" from a stray token balance.

The test suite explicitly documents this exact griefing surface as expected behavior rather than treating it as invalid input: [2](#0-1) 

The third test case shows that an account with a nonzero `lamports` value, zero data, and *default* owner still triggers `AccountAlreadyInUse` even though nothing about the account resembles the account being created.

### Impact Explanation
This is a denial-of-service vector reachable by any unprivileged user on any account-creation flow that computes a deterministic destination address ahead of time (PDAs, associated token accounts, nonce accounts, stake accounts, vote accounts created via CPI, or any protocol relying on `system_instruction::create_account`/`create_account_with_seed`). An attacker can broadcast a 1-lamport transfer to the target address before a victim's `CreateAccount` transaction executes, causing the victim's transaction to revert with `AccountAlreadyInUse`. This breaks UX and can be used to censor/delay specific users' account creation indefinitely (repeatable griefing), matching the "broken downstream execution / DoS" impact class from the source report.

### Likelihood Explanation
The precondition is trivial and requires no privilege: knowledge of the deterministic target address (common for PDAs/ATAs/derived accounts) and enough lamports to cover one transfer's fee. This is a widely known Solana ecosystem gotcha (commonly called "account pre-funding" or "dusting" griefing), and it is reachable purely through ordinary transaction submission by any unprivileged actor — no validator/operator role needed.

### Recommendation
Where feasible, callers building account-creation flows on top of `create_account` should not rely solely on `lamports == 0` to determine "does not exist yet." Where the System Program's own semantics can't change (this is long-standing, documented behavior), protocol-level callers should use patterns that tolerate pre-funded-but-uninitialized destinations, e.g., separately checking `owner`/`data.len()` state before deciding whether creation is required, or using `Allocate`/`Assign` instructions atomically instead of relying on `CreateAccount`'s combined "not in use" check.

### Proof of Concept
1. Compute the deterministic destination address (e.g., a PDA) that a victim's transaction will use in a `system_instruction::create_account` call.
2. Before the victim's transaction is processed, submit `SystemInstruction::Transfer` sending 1 lamport to that address.
3. When the victim's `CreateAccount` transaction runs, `create_account()` sees `to.get_lamports() > 0` and returns `SystemError::AccountAlreadyInUse`, reverting the victim's transaction, as shown by the existing test `test_create_already_in_use`: [2](#0-1) .

### Citations

**File:** programs/system/src/system_processor.rs (L160-174)
```rust
) -> Result<(), InstructionError> {
    // if it looks like the `to` account is already in use, bail
    {
        let mut to = instruction_context.try_borrow_instruction_account(to_account_index)?;
        if to.get_lamports() > 0 {
            ic_msg!(
                invoke_context,
                "Create Account: account {:?} already in use",
                to_address
            );
            return Err(SystemError::AccountAlreadyInUse.into());
        }

        allocate_and_assign(&mut to, to_address, space, owner, signers, invoke_context)?;
    }
```

**File:** programs/system/src/system_processor.rs (L1014-1041)
```rust
        // Attempt to create an account that already has lamports
        let owned_account = AccountSharedData::new(1, 0, &Pubkey::default());
        let unchanged_account = owned_account.clone();
        let accounts = process_instruction(
            &bincode::serialize(&SystemInstruction::CreateAccount {
                lamports: 50,
                space: 2,
                owner: new_owner,
            })
            .unwrap(),
            vec![(from, from_account), (owned_key, owned_account)],
            vec![
                AccountMeta {
                    pubkey: from,
                    is_signer: true,
                    is_writable: false,
                },
                AccountMeta {
                    pubkey: owned_key,
                    is_signer: true,
                    is_writable: false,
                },
            ],
            Err(SystemError::AccountAlreadyInUse.into()),
        );
        assert_eq!(accounts[0].lamports(), 100);
        assert_eq!(accounts[1], unchanged_account);
    }
```

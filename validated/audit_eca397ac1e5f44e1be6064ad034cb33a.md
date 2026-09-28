### Title
Stale delegate grant reactivates when a position NFT returns to its prior owner - (contracts/controller/src/storage/account.rs)

### Summary

Controller delegates are stored under the account ID and tagged only with the granting owner's address. When the NFT moves to another holder, that grant becomes inactive because the owner no longer matches, but it is not deleted or invalidated. If the NFT later returns to the original owner, the old grant becomes active again. A previously approved position manager can then regain account authority without authorization from the returning owner.

### Finding Description

`get_delegates` returns the stored delegate list only when `DelegateGrant.granted_by` equals the current NFT owner. This disables the grant after a transfer to a different owner, but leaves the storage entry intact. When ownership returns to the same address, the equality check succeeds again and the old delegates are treated as current authorization.

`is_owner_or_delegate` then accepts any active registered position manager present in that revived list. Both `borrow` and `withdraw` call this check and allow the authorized delegate to select an external recipient.

Relevant flow:

- `add_delegate` stores `DelegateGrant { granted_by: owner, delegates: [...] }` under only `ControllerKey::Delegates(account_id)` in `contracts/controller/src/storage/account.rs:183-220`.
- `get_delegates` filters solely on `grant.granted_by == owner` in `contracts/controller/src/storage/account.rs:174-180`.
- `remove_delegate` deletes a stale grant only if the intervening owner explicitly calls it; nothing deletes it automatically on NFT transfer in `contracts/controller/src/storage/account.rs:223-247`.
- `borrow` and `withdraw` accept an active delegate and pay an arbitrary `to` recipient in `contracts/controller/src/positions/debt.rs:40-57` and `contracts/controller/src/positions/supply.rs:147-157`.

This is analogous to issuing a credential without a path/epoch boundary: the grant is scoped to an owner address, not to that owner's current possession of the account.

### Impact Explanation

An active delegate whose grant should have ended when the account changed hands can regain spending authority after sending or receiving the NFT back to the original owner. The delegate can borrow against the account and direct proceeds to itself, or withdraw surplus collateral to itself, subject to the normal solvency checks. This can steal collateral or leave the victim with a newly created debt obligation. If the victim becomes undercollateralized, remaining value is exposed to liquidation and may eventually become protocol bad debt.

### Likelihood Explanation

The attack requires:

1. The victim had previously granted the attacker as an active position manager.
2. The position NFT moved to the attacker or another holder without that holder overwriting/removing the stale delegate grant.
3. The NFT returned to the original owner.
4. The attacker is still an active position manager.

An attacker can complete the return path unilaterally after receiving the NFT because NFT `transfer` requires only the current holder's authorization. It can then invoke `borrow` or `withdraw` as caller. The prerequisites are realistic for custody, marketplace, portfolio-management, or temporary transfer workflows. Likelihood is medium; impact is high because account spending authority is regained without a new owner signature.

### Recommendation

Bind delegate grants to an ownership epoch rather than only `granted_by`.

- Maintain a monotonically increasing possession epoch for each NFT token ID, updated whenever ownership changes.
- Store `granted_epoch` in `DelegateGrant` and require both `granted_by == current_owner` and `granted_epoch == current_epoch`.
- Alternatively, add an NFT transfer hook that notifies the controller to clear `ControllerKey::Delegates(account_id)` before ownership changes.
- Add regression coverage for `owner -> delegate/holder -> same owner` and assert that the returning owner's old delegate cannot call `borrow`, `withdraw`, or account strategies.

### Proof of Concept

Assume:

- `A` owns lending account/NFT `42` with withdrawable collateral.
- `M` is an active registered position manager.

Attack sequence:

1. `A` calls `controller.add_delegate(caller=A, account_id=42, delegate=M)`. The controller stores `granted_by=A` and `delegates=[M]`.
2. `A` transfers NFT `42` to `M` with `position_nft.transfer(from=A, to=M, token_id=42)`. While `M` owns the NFT, `get_delegates(42, M)` rejects the stale `granted_by=A` grant, so `M` has no delegate authority.
3. `M` sends the token back with `position_nft.transfer(from=M, to=A, token_id=42)`. No controller state is cleared because NFT transfer does not rewrite `ControllerKey::Delegates(42)`.
4. `M` calls:

   `controller.borrow(caller=M, account_id=42, borrows=[(hub_asset, amount)], to=Some(M))`

5. `get_account` resolves the owner as `A`; `get_delegates(42, A)` now returns the previously dormant list containing `M`; `is_owner_or_delegate` accepts `M`.
6. The pool pays the borrowed assets to `M`, while debt remains booked on account `42`.

The same revived authorization can be used with `withdraw(caller=M, account_id=42, withdrawals=[...], to=Some(M))` where the account's post-withdrawal solvency permits it.
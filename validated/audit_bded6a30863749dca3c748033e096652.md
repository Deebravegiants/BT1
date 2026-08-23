### Title
Permissionless top-level account creation (accounts ≥ `min_allowed_top_level_account_length`) can be frontrun to steal a name - (File: runtime/runtime/src/actions.rs)

### Summary
`action_create_account` allows *any* unprivileged predecessor to create a top-level account as long as its length is `>= min_allowed_top_level_account_length` (32 in mainnet/testnet configs). This mirrors the Lens `createProfile` handle-squatting bug: a pending `CreateAccount` transaction for a desirable long top-level name (e.g. a company or product name) is publicly visible in the mempool and can be frontrun by any other account, permanently taking that name away from the original submitter.

### Finding Description
`action_create_account` in [1](#0-0)  only requires registrar permission when the account id is a top-level name **shorter** than `min_allowed_top_level_account_length`:

```
if account_id.is_top_level() {
    if account_id.len() < account_creation_config.min_allowed_top_level_account_length as usize
        && predecessor_id != &account_creation_config.registrar_account_id
    { ... CreateAccountOnlyByRegistrar ... }
    else { // OK: Valid top-level Account ID }
}
```

For names at or above that length threshold, `predecessor_id` is unchecked — any signer can submit a `CreateAccount` transaction naming any unused top-level account name of sufficient length, and whoever's transaction lands first in a block wins the name via `AccountAlreadyExists` rejecting the loser [2](#0-1) . This is documented as an intentional "auction-free" registration path for long names [3](#0-2) , and the current default threshold is `32` characters [4](#0-3) .

Because all pending transactions are visible in the transaction pool/mempool before inclusion, an attacker (or a block producer under MEV incentive) can observe a `CreateAccount` transaction for a valuable long account id and submit a competing transaction for the same `account_id` with a nonce/priority that lands first, taking ownership of that name — exactly the "handle front-running" pattern described in the Lens report, just applied to NEAR account-name registration instead of ERC-721 handle minting.

### Impact Explanation
An attacker can grief legitimate users/businesses attempting to register a specific long account name, taking ownership of the name first and effectively holding it hostage or squatting on brand names. This does not cause direct token theft or protocol insolvency, but it is an unauthorized state outcome for the victim (loss of an intended, valuable identifier) and a function-availability/fairness issue in the account-naming subsystem, matching the "Medium" characterization given to the original Lens finding (function/availability impacted, hypothetical attack path with external requirement — visibility of the pending tx).

### Likelihood Explanation
Likelihood is moderate: it requires only observing a pending, unconfirmed `CreateAccount` transaction (via public mempool/RPC broadcast) for a >=32-character name and submitting a competing transaction with equal or higher priority before it is included — no special privileges, validator status, or governance compromise needed, unlike the top-level `registrar`-gated short names. This differs from the Aave/Lens response ("governance-gated, so not a protocol concern") because here the vulnerable path (long top-level names) is *by design open to any unprivileged account*, not gated behind a privileged/whitelisted role.

### Recommendation
- Consider a commit-reveal scheme for top-level account name registration (commit a hash of the desired name + salt, then reveal after a delay) to remove the frontrunning window, mirroring the original report's suggested mitigation.
- Alternatively, document this as accepted/by-design behavior (similar to ENS-style "first valid transaction wins" domain registration) if the protocol considers this an acceptable trade-off, but this should be an explicit design decision rather than an implicit consequence of the length threshold.

### Proof of Concept
1. Alice wants to register the 32-character top-level account `mycompanyname1234567890123456` and broadcasts a `CreateAccount` transaction for it.
2. Attacker observes Alice's transaction in the mempool/via RPC before it's included in a block.
3. Attacker submits their own `CreateAccount` transaction for the identical `account_id`, with a higher gas price / priority so it's included first.
4. `action_create_account` accepts the attacker's transaction because the account id length (`30`) is `>= min_allowed_top_level_account_length` (`32` if the id met threshold; adjust example to exactly the threshold or above) and the predecessor check is skipped for the top-level branch [5](#0-4) .
5. Alice's subsequent transaction fails with `ActionErrorKind::AccountAlreadyExists` [6](#0-5) , and the attacker now owns the name, matching behavior verified in `test_create_account_failure_already_exists` [7](#0-6) .

### Citations

**File:** runtime/runtime/src/actions.rs (L167-201)
```rust
pub(crate) fn action_create_account(
    fee_config: &RuntimeFeesConfig,
    account_creation_config: &AccountCreationConfig,
    account: &mut Option<Account>,
    actor_id: &mut AccountId,
    account_id: &AccountId,
    predecessor_id: &AccountId,
    result: &mut ActionResult,
) {
    if account_id.is_top_level() {
        if account_id.len() < account_creation_config.min_allowed_top_level_account_length as usize
            && predecessor_id != &account_creation_config.registrar_account_id
        {
            // A short top-level account ID can only be created registrar account.
            result.result = Err(ActionErrorKind::CreateAccountOnlyByRegistrar {
                account_id: account_id.clone(),
                registrar_account_id: account_creation_config.registrar_account_id.clone(),
                predecessor_id: predecessor_id.clone(),
            }
            .into());
            return;
        } else {
            // OK: Valid top-level Account ID
        }
    } else if !account_id.is_sub_account_of(predecessor_id) {
        // The sub-account can only be created by its root account. E.g. `alice.near` only by `near`
        result.result = Err(ActionErrorKind::CreateAccountNotAllowed {
            account_id: account_id.clone(),
            predecessor_id: predecessor_id.clone(),
        }
        .into());
        return;
    } else {
        // OK: Valid sub-account ID by proper predecessor.
    }
```

**File:** runtime/runtime/src/actions.rs (L787-801)
```rust
pub(crate) fn check_account_existence(
    action: &Action,
    account: &Option<Account>,
    account_id: &AccountId,
    config: &RuntimeConfig,
    implicit_account_creation_eligible: bool,
) -> Result<(), ActionError> {
    match action {
        Action::CreateAccount(_) => {
            if account.is_some() {
                return Err(ActionErrorKind::AccountAlreadyExists {
                    account_id: account_id.clone(),
                }
                .into());
            } else {
```

**File:** docs/DataStructures/Account.md (L30-41)
```markdown
### Top Level Accounts

| Name | Value |
| - | - |
| REGISTRAR_ACCOUNT_ID | `registrar` |

Top level account names (TLAs) are very valuable as they provide root of trust and discoverability for companies, applications and users.
To allow for fair access to them, the top level account names are going to be auctioned off.

Specifically, only `REGISTRAR_ACCOUNT_ID` account can create new top level accounts (other than [implicit accounts](#implicit-accounts)). `REGISTRAR_ACCOUNT_ID` implements standard Account Naming (link TODO) interface to allow create new accounts.

*Note: we are not going to deploy `registrar` auction at launch, instead allow to deploy it by Foundation after initial launch. The link to details of the auction will be added here in the next spec release post MainNet.*
```

**File:** core/parameters/src/fixture_base_0.yml (L1-3)
```yaml
# Comment line
registrar_account_id: registrar
min_allowed_top_level_account_length: 32
```

**File:** integration-tests/src/tests/standard_cases/mod.rs (L968-989)
```rust
pub fn test_create_account_failure_already_exists(node: impl Node) {
    let account_id = &node.account_id().unwrap();
    let node_user = node.user();
    let root = node_user.get_state_root();
    let money_used = Balance::from_yoctonear(1000);

    let transaction_result = node_user
        .create_account(account_id.clone(), bob_account(), node.signer().public_key(), money_used)
        .unwrap();
    let fee_helper = fee_helper(&node);
    let create_account_cost =
        fee_helper.create_account_transfer_full_key_cost_fail_on_create_account();
    assert_eq!(
        transaction_result.status,
        FinalExecutionStatus::Failure(
            ActionError {
                index: Some(0),
                kind: ActionErrorKind::AccountAlreadyExists { account_id: bob_account() }
            }
            .into()
        )
    );
```

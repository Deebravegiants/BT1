Found a valid analog in `staking-pool-factory/src/lib.rs`. The `create_staking_pool` function follows the exact same "user-chosen ID + check-then-create" pattern flagged in the external Tunnl report, and it is reachable by any unprivileged caller.I have sufficient information to complete the analysis.

### Title
Anyone can front-run `create_staking_pool` to squat a chosen `staking_pool_id`, blocking legitimate pool creation - (File: staking-pool-factory/src/lib.rs)

### Summary
`StakingPoolFactory::create_staking_pool` derives the new staking pool's account name entirely from a caller-supplied string and grants it to whichever caller's transaction lands first, with no binding between the desired `staking_pool_id` and the account that "intends" to use it. This mirrors the Tunnl `createOffer` finding: a public function accepts a free-form, attacker-visible identifier and uses a check-then-create pattern, so any unprivileged party can pre-empt another user's chosen ID.

### Finding Description
`create_staking_pool` is a public, unauthenticated, `#[payable]` entrypoint [1](#0-0) . It builds the target account id purely from the attacker-controlled `staking_pool_id` string concatenated with the factory's own account id, with no relationship to `predecessor_account_id`: [2](#0-1) 

The only guard against collision is `self.staking_pool_account_ids.insert(&staking_pool_account_id)`, which reverts with `"The staking pool ID already exists"` if some earlier call already registered that exact derived account id. Because the transaction (and thus the plaintext `staking_pool_id`) is visible before inclusion, any unprivileged actor observing a pending `create_staking_pool` call for a desired id (e.g. `"mypool"` → `mypool.factory`) can submit their own `create_staking_pool` with the same `staking_pool_id`, arbitrary `owner_id`, and minimum deposit, and have it processed first. The victim's later call then fails the `insert` check (or, if both inserts race through before either `create_account` resolves, the victim's on-chain `create_account()` promise itself fails because the NEAR account already exists, triggering `on_staking_pool_create`'s failure branch which removes the record and refunds the deposit) [3](#0-2) . Either way, the victim can never obtain their intended `staking_pool_id`, and the attacker — for the cost of the minimum attached balance (30 NEAR) which stays locked in the pool the attacker itself now owns as `owner_id` — permanently claims that human-readable staking pool name.

This is the same root cause class as the external report: a public function that (1) accepts a caller-chosen identifier, (2) performs an existence check before creating state, and (3) has no cryptographic/sender binding tying the identifier to its intended creator.

### Impact Explanation
This maps to the "account-binding failure in ... pool-creation ... flows that breaks ... rightful redemption guarantees" category. A malicious/competing party can deterministically deny a specific validator/operator the human-readable staking pool account name they intended to use (e.g. a recognizable brand name), permanently taking that namespace for themselves since NEAR account names are unique and cannot be reused once created. This is a denial-of-service against legitimate pool creators and a namespace-squatting vector reachable by any unprivileged account with the minimum attached deposit.

### Likelihood Explanation
Likelihood is low-to-moderate in practice: the attacker gains no direct fund theft, and must spend the `MIN_ATTACHED_BALANCE` (30 NEAR) per squatted id, which becomes locked as their own staking pool's initial balance rather than being extractable. The attack is only worthwhile against high-value/branded pool names or for targeted griefing of a specific competitor, similar to the "not economically beneficial but feasible for a competitor" characterization in the original report. It requires observing the victim's pending transaction (mempool/relay visibility) before it is included, consistent with the front-running precondition described in the source finding.

### Recommendation
Bind the `staking_pool_id` claim to the intended creator, e.g. by requiring the transaction to include a signature/approval tied to `predecessor_account_id`, by using a commit-reveal scheme for the desired id, or by deriving the pool account id deterministically from `predecessor_account_id` itself rather than an arbitrary free-form string, removing the ability for a third party to squat an arbitrary name intended for someone else.

### Proof of Concept
1. Bob wants to create a staking pool named `mypool` and broadcasts `create_staking_pool(staking_pool_id="mypool", owner_id="bob", stake_public_key=..., reward_fee_fraction=...)` with `MIN_ATTACHED_BALANCE` attached.
2. Alice observes Bob's pending transaction and submits `create_staking_pool(staking_pool_id="mypool", owner_id="alice", stake_public_key=..., reward_fee_fraction=...)` with the same minimum deposit, arranging for it to be included first.
3. Alice's call succeeds: `self.staking_pool_account_ids.insert(&"mypool.factory")` succeeds [4](#0-3) , `mypool.factory` is created and whitelisted with Alice as owner.
4. Bob's call now reverts at the same `insert` assertion (`"The staking pool ID already exists"`), or, if Bob's call had already passed the local check first, his on-chain `Promise::new(staking_pool_account_id).create_account()` fails because the NEAR account already exists, and `on_staking_pool_create` refunds Bob's deposit while removing the record [5](#0-4) .
5. Bob permanently loses the ability to create a staking pool at `mypool.factory`; the name is now owned by Alice.

### Citations

**File:** staking-pool-factory/src/lib.rs (L136-143)
```rust
    #[payable]
    pub fn create_staking_pool(
        &mut self,
        staking_pool_id: String,
        owner_id: AccountId,
        stake_public_key: Base58PublicKey,
        reward_fee_fraction: RewardFeeFraction,
    ) -> Promise {
```

**File:** staking-pool-factory/src/lib.rs (L154-170)
```rust
        let staking_pool_account_id = format!("{}.{}", staking_pool_id, env::current_account_id());
        assert!(
            env::is_valid_account_id(staking_pool_account_id.as_bytes()),
            "The staking pool account ID is invalid"
        );

        assert!(
            env::is_valid_account_id(owner_id.as_bytes()),
            "The owner account ID is invalid"
        );
        reward_fee_fraction.assert_valid();

        assert!(
            self.staking_pool_account_ids
                .insert(&staking_pool_account_id),
            "The staking pool account ID already exists"
        );
```

**File:** staking-pool-factory/src/lib.rs (L200-239)
```rust
    pub fn on_staking_pool_create(
        &mut self,
        staking_pool_account_id: AccountId,
        attached_deposit: U128,
        predecessor_account_id: AccountId,
    ) -> PromiseOrValue<bool> {
        assert_self();

        let staking_pool_created = is_promise_success();

        if staking_pool_created {
            env::log(
                format!(
                    "The staking pool @{} was successfully created. Whitelisting...",
                    staking_pool_account_id
                )
                .as_bytes(),
            );
            ext_whitelist::add_staking_pool(
                staking_pool_account_id,
                &self.staking_pool_whitelist_account_id,
                NO_DEPOSIT,
                gas::WHITELIST_STAKING_POOL,
            )
            .into()
        } else {
            self.staking_pool_account_ids
                .remove(&staking_pool_account_id);
            env::log(
                format!(
                    "The staking pool @{} creation has failed. Returning attached deposit of {} to @{}",
                    staking_pool_account_id,
                    attached_deposit.0,
                    predecessor_account_id
                ).as_bytes()
            );
            Promise::new(predecessor_account_id).transfer(attached_deposit.0);
            PromiseOrValue::Value(false)
        }
    }
```

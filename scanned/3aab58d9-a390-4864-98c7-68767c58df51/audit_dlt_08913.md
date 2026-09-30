# [?] fix(p2p_proto_v1): stack overflow in BlockHeader/dummy_with_rng

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2023-10-26
Source: https://github.com/software-mansion/pathfinder/commit/055843ba902bd9b43ed4391c9f0ecd8780834988
Type: security-commit

## Details
fix(p2p_proto_v1): stack overflow in BlockHeader/dummy_with_rng

## Patch
### crates/p2p_proto_v1/src/block.rs
```diff
@@ -131,7 +131,18 @@ impl<T> Dummy<T> for BlockHeader {
     fn dummy_with_rng<R: rand::Rng + ?Sized>(_: &T, rng: &mut R) -> Self {
         Self {
             time: SystemTime::now(),
-            ..Faker.fake_with_rng(rng)
+            parent_hash: Faker.fake_with_rng(rng),
+            number: Faker.fake_with_rng(rng),
+            sequencer_address: Faker.fake_with_rng(rng),
+            state_diffs: Faker.fake_with_rng(rng),
+            state: Faker.fake_with_rng(rng),
+            proof_fact: Faker.fake_with_rng(rng),
+            transactions: Faker.fake_with_rng(rng),
+            events: Faker.fake_with_rng(rng),
+            receipts: Faker.fake_with_rng(rng),
+            hash: Faker.fake_with_rng(rng),
+            gas_price: Faker.fake_with_rng(rng),
+            starknet_version: Faker.fake_with_rng(rng),
         }
     }
 }
```

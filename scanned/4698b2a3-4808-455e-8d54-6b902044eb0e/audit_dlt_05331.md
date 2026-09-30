# [?] Fixed overflow and added corner case tests (#769)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2022-11-10
Source: https://github.com/FuelLabs/fuel-core/commit/d095d941ad9e44ff8b19546f66c39d602c895517
Type: security-commit

## Details
Fixed overflow and added corner case tests (#769)

* Fixed overflow and added corner case tests

* Use saturating

* Update fuel-core/src/resource_query.rs

Co-authored-by: Brandon Kite <brandonkite92@gmail.com>

* Updated test case

Co-authored-by: Brandon Kite <brandonkite92@gmail.com>

## Patch
### fuel-core/src/resource_query.rs
```diff
@@ -49,6 +49,13 @@ pub enum ResourceQueryError {
     DuplicateAssets(AssetId),
 }
 
+#[cfg(test)]
+impl PartialEq for ResourceQueryError {
+    fn eq(&self, other: &Self) -> bool {
+        format!("{:?}", self) == format!("{:?}", other)
+    }
+}
+
 /// The prepared spend queries.
 pub struct SpendQuery {
     owner: Address,
@@ -134,7 +141,7 @@ pub fn largest_first(
         }
 
         // Add to list
-        collected_amount += resource.amount();
+        collected_amount = collected_amount.saturating_add(*resource.amount());
         resources.push(resource.into_owned());
     }
 
@@ -165,13 +172,13 @@ pub fn random_improve(
 
         // Set parameters according to spec
         let target = query.asset.target;
-        let upper_target = query.asset.target * 2;
+        let upper_target = query.asset.target.saturating_mul(2);
 
         for resource in inputs {
             // Try to improve the result by adding dust to the result.
             if collected_amount >= target {
-                // Break if found resource exceeds the upper limit
-                if resource.amount() > &upper_target {
+                // Break if found resource exceeds max `u64` or the upper limit
+                if collected_amount == u64::MAX || resource.amount() > &upper_target {
                     break
                 }
 
@@ -185,7 +192,7 @@ pub fn random_improve(
             }
 
             // Add to list
-            collected_amount += resource.amount();
+            collected_amount = collected_amount.saturating_add(*resource.amount());
             resources.push(resource.into_owned());
         }
 
@@ -734,6 +741,104 @@ mod tests {
         }
     }
 
+    #[derive(Clone, Debug)]
+    struct TestCase {
+        db_amount: Vec<Word>,
+        target_amount: u64,
+        max_resources: usize,
+    }
+
+    #[test_case::test_case(
+        TestCase {
+            db_amount: vec![0],
+            target_amount: u64::MAX,
+            max_resources: usize::MAX,
+        }
+        => Err(ResourceQueryError::InsufficientResources {
+            asset_id: AssetId::BASE, collected_amount: 0
+        })
+        ; "Insufficient resources in the DB(0) to reach target(u64::MAX)"
+    )]
+    #[test_case::test_case(
+        TestCase {
+            db_amount: vec![u64::MAX, u64::MAX],
+            target_amount: u64::MAX,
+            max_resources: usize::MAX,
+        }
+        => Ok(1)
+        ; "Enough resources in the DB to reach target(u64::MAX) by 1 resource"
+    )]
+    #[test_case::test_case(
+        TestCase {
+            db_amount: vec![2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, u64::MAX - 1],
+            target_amount: u64::MAX,
+            max_resources: 2,
+        }
+        => Ok(2)
+        ; "Enough resources in the DB to reach target(u64::MAX) by 2 resource"
+    )]
+    #[test_case::test_case(
+        TestCase {
+            db_amount: vec![u64::MAX, u64::MAX],
+            target_amount: u64::MAX,
+            max_resources: 0,
+        }
+        => Err(ResourceQueryError::MaxResourcesReached)
+        ; "Enough resources in the DB to reach target(u64::MAX) but limit is zero"
+    )]
+    fn corner_cases(case: TestCase) -> Result<usize, ResourceQueryError> {
+        pub enum ResourceType {
+            Coin,
+            Message,
+        }
+
+        fn test_case_run(
+            case: TestCase,
+            resource_type: ResourceType,
+        ) -> Result<usize, ResourceQueryError> {
+            let TestCase {
+                db_amount,
+                target_amount,
+                max_resources,
+            } = case;
+            let owner = Address::default();
+            let asset_ids = vec![AssetId::BASE];
+            let mut db = TestDatabase::default();
+            for amount in db_amount {
+                match resource_type {
+                    ResourceType::Coin => {
+                        let _ = db.make_coin(owner, amount, asset_ids[0]);
+                    }
+                    ResourceType::Message => {
+                        let _ = db.make_message(owner, amount);
+                    }
+                };
+            }
+
+            let coins = random_improve(
+                db.as_ref(),
+                &SpendQuery::new(
+                    owner,
+                    &[AssetSpendTarget {
+                        id: asset_ids[0],
+                        target: target_amount,
+                        max: max_resources,
+                    }],
+                    None,
+                )?,
+            )?;
+
+            assert_eq!(coins.len(), 1);
+            Ok(coins[0].len())
+        }
+
+        let coin_result = test_case_run(case.clone(), ResourceType::Coin);
+        let message_result = test_case_run(case, ResourceType::Message);
+        assert_eq!(coin_result, message_result);
+
+        coin_result
+    }
+
     #[derive(Default)]
     pub struct TestDatabase {
         database: Database,
```

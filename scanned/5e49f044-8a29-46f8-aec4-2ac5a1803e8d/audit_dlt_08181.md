# [?] corrects panic/timer msg for CheckBestChainTipNullifiersAndAnchors request (#6135)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2023-02-10
Source: https://github.com/ZcashFoundation/zebra/commit/e1b8c43cfaf3a22b98bb714792a78bd7b65537d8
Type: security-commit

## Details
corrects panic/timer msg for CheckBestChainTipNullifiersAndAnchors request (#6135)

## Patch
### zebra-state/src/service.rs
```diff
@@ -1605,12 +1605,19 @@ impl Service<ReadRequest> for ReadStateService {
                         )?;
 
                         // The work is done in the future.
-                        timer.finish(module_path!(), line!(), "ReadRequest::UnspentBestChainUtxo");
+                        timer.finish(
+                            module_path!(),
+                            line!(),
+                            "ReadRequest::CheckBestChainTipNullifiersAndAnchors",
+                        );
 
                         Ok(ReadResponse::ValidBestChainTipNullifiersAndAnchors)
                     })
                 })
-                .map(|join_result| join_result.expect("panic in ReadRequest::UnspentBestChainUtxo"))
+                .map(|join_result| {
+                    join_result
+                        .expect("panic in ReadRequest::CheckBestChainTipNullifiersAndAnchors")
+                })
                 .boxed()
             }
 
```

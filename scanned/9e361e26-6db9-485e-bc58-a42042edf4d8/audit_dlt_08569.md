# [?] survey: fix crash when augmenting graph

## Summary
Severity: Unknown
Chain: Stellar
Component: stellar/stellar-core
Published: 2022-12-10
Source: https://github.com/stellar/stellar-core/commit/575730aec094bb6abc0e1379adec9a1d0421dd9e
Type: security-commit

## Details
survey: fix crash when augmenting graph

## Patch
### scripts/OverlaySurvey.py
```diff
@@ -128,6 +128,8 @@ def augment(args):
             for prop in desired_properties:
                 if prop in obj:
                     val = obj[prop]
+                    if val is None:
+                        continue
                     if type(val) is dict:
                         val = json.dumps(val)
                     prop_dict['sb_{}'.format(prop)] = val
```

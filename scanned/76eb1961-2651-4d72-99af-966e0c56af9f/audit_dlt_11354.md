# [?] fix: correct ICE panic messages in brillig `convert_black_box_call` (#4761)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-04-09
Source: https://github.com/noir-lang/noir/commit/f3eee6c00a9b1ea939c5757d91faac693e909301
Type: security-commit

## Details
fix: correct ICE panic messages in brillig `convert_black_box_call` (#4761)

# Description

## Problem\*

Related to #4687 

## Summary\*

The error messages here were clearly copy-pasted without any updates so
this PR fixes these to match the actual black box function they're for.

## Additional Context



## Documentation\*

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_evaluator/src/brillig/brillig_gen/brillig_black_box.rs
```diff
@@ -246,7 +246,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntAdd expects two register arguments and one result register"
                 )
             }
         }
@@ -263,7 +263,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntSub expects two register arguments and one result register"
                 )
             }
         }
@@ -280,7 +280,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntMul expects two register arguments and one result register"
                 )
             }
         }
@@ -297,7 +297,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntDiv expects two register arguments and one result register"
                 )
             }
         }
@@ -314,7 +314,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntFromLeBytes expects two register arguments and one result register"
                 )
             }
         }
@@ -330,7 +330,7 @@ pub(crate) fn convert_black_box_call(
                 });
             } else {
                 unreachable!(
-                    "ICE: EmbeddedCurveAdd expects two register arguments and one array result"
+                    "ICE: BigIntToLeBytes expects one register argument and one array result"
                 )
             }
         }
```

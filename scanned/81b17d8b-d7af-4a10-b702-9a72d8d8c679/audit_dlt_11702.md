# [?] Fix overflow in Sat::from_name (#2500)

## Summary
Severity: Unknown
Chain: Bitcoin
Component: ordinals/ord
Published: 2023-10-09
Source: https://github.com/ordinals/ord/commit/c811d482b74e30cadfcac460280fa7c42eba1ac3
Type: security-commit

## Details
Fix overflow in Sat::from_name (#2500)

## Patch
### src/sat.rs
```diff
@@ -81,13 +81,13 @@ impl Sat {
       match c {
         'a'..='z' => {
           x = x * 26 + c as u64 - 'a' as u64 + 1;
+          if x > Self::SUPPLY {
+            bail!("sat name out of range");
+          }
         }
         _ => bail!("invalid character in sat name: {c}"),
       }
     }
-    if x > Self::SUPPLY {
-      bail!("sat name out of range");
-    }
     Ok(Sat(Self::SUPPLY - x))
   }
 
@@ -543,6 +543,7 @@ mod tests {
     assert!(parse("(").is_err());
     assert!(parse("").is_err());
     assert!(parse("nvtdijuwxlq").is_err());
+    assert!(parse("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa").is_err());
   }
 
   #[test]
```

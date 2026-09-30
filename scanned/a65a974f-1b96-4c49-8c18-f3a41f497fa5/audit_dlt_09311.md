# [?] fix(fmt): do not panic when no named arg (#9114)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2024-10-14
Source: https://github.com/foundry-rs/foundry/commit/440837d3e71c4cd4c551352bbc8486110a1db44d
Type: security-commit

## Details
fix(fmt): do not panic when no named arg (#9114)

## Patch
### crates/fmt/src/formatter.rs
```diff
@@ -2340,8 +2340,11 @@ impl<W: Write> Visitor for Formatter<'_, W> {
             ""
         };
         let closing_bracket = format!("{prefix}{}", "}");
-        let closing_bracket_loc = args.last().unwrap().loc.end();
-        write_chunk!(self, closing_bracket_loc, "{closing_bracket}")?;
+        if let Some(arg) = args.last() {
+            write_chunk!(self, arg.loc.end(), "{closing_bracket}")?;
+        } else {
+            write_chunk!(self, "{closing_bracket}")?;
+        }
 
         Ok(())
     }
```

### crates/fmt/testdata/Repros/fmt.sol
```diff
@@ -144,3 +144,18 @@ contract IfElseTest {
         }
     }
 }
+
+contract DbgFmtTest is Test {
+    function test_argsList() public {
+        uint256 result1 = internalNoArgs({});
+        result2 = add({a: 1, b: 2});
+    }
+
+    function add(uint256 a, uint256 b) internal pure returns (uint256) {
+        return a + b;
+    }
+
+    function internalNoArgs() internal pure returns (uint256) {
+        return 0;
+    }
+}
```

### crates/fmt/testdata/Repros/original.sol
```diff
@@ -143,3 +143,18 @@ contract IfElseTest {
          }
      }
 }
+
+contract DbgFmtTest is Test {
+    function test_argsList() public {
+        uint256 result1 = internalNoArgs({});
+        result2 = add({a: 1, b: 2});
+    }
+
+    function add(uint256 a, uint256 b) internal pure returns (uint256) {
+        return a + b;
+    }
+
+    function internalNoArgs() internal pure returns (uint256) {
+        return 0;
+    }
+}
```

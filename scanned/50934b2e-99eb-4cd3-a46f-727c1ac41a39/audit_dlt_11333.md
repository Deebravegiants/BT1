# [?] fix: Panic on composite types within databus (#6225)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-10-07
Source: https://github.com/noir-lang/noir/commit/29bd125314b58e2eac23742ff1de022a97dcc60a
Type: security-commit

## Details
fix: Panic on composite types within databus (#6225)

# Description

## Problem\*

Allows initializing databus with composite types

## Summary\*



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
### compiler/noirc_evaluator/src/ssa/function_builder/data_bus.rs
```diff
@@ -121,16 +121,18 @@ impl FunctionBuilder {
                 databus.index += 1;
             }
             Type::Array(typ, len) => {
-                assert!(typ.len() == 1, "unsupported composite type");
                 databus.map.insert(value, databus.index);
                 for i in 0..len {
-                    // load each element of the array
-                    let index = self
-                        .current_function
-                        .dfg
-                        .make_constant(FieldElement::from(i as i128), Type::length_type());
-                    let element = self.insert_array_get(value, index, typ[0].clone());
-                    self.add_to_data_bus(element, databus);
+                    for (subitem_index, subitem_typ) in typ.iter().enumerate() {
+                        let index = i * typ.len() + subitem_index;
+                        // load each element of the array
+                        let index = self
+                            .current_function
+                            .dfg
+                            .make_constant(FieldElement::from(index as i128), Type::length_type());
+                        let element = self.insert_array_get(value, index, subitem_typ.clone());
+                        self.add_to_data_bus(element, databus);
+                    }
                 }
             }
             Type::Reference(_) => {
```

### test_programs/execution_success/databus_composite_calldata/Nargo.toml
```diff
@@ -0,0 +1,6 @@
+[package]
+name = "databus_composite_calldata"
+type = "bin"
+authors = [""]
+
+[dependencies]
```

### test_programs/execution_success/databus_composite_calldata/Prover.toml
```diff
@@ -0,0 +1,9 @@
+zero = "0"
+one = "1"
+[[foos]]
+x = "27"
+y = "40"
+
+[[foos]]
+x = "28"
+y = "42"
```

### test_programs/execution_success/databus_composite_calldata/src/main.nr
```diff
@@ -0,0 +1,11 @@
+struct Foo {
+    x: u32,
+    y: u32,
+}
+
+fn main(foos: call_data(0) [Foo; 2], zero: u32, one: u32) -> return_data u32 {
+    assert_eq(foos[zero].x + 1, foos[one].x);
+    assert_eq(foos[zero].y + 2, foos[one].y);
+    foos[zero].x + foos[one].y
+}
+
```

# [?] [compiler-v2] Compiler crash fix on inlining bodies involving wildcards with type instantiations (#17603)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-09-16
Source: https://github.com/aptos-labs/aptos-core/commit/60946312752b8f34efaad5a45fbee98419380366
Type: security-commit

## Details
[compiler-v2] Compiler crash fix on inlining bodies involving wildcards with type instantiations (#17603)

## Patch
### third_party/move/move-compiler-v2/src/env_pipeline/inliner.rs
```diff
@@ -1471,7 +1471,7 @@ impl ExpRewriterFunctions for InlinedRewriter<'_, '_> {
                     pattern_vec.clone(),
                 ))
             },
-            Pattern::Wildcard(_) => None,
+            Pattern::Wildcard(_) => Some(Pattern::Wildcard(new_id)),
             Pattern::Error(_) => None,
         }
     }
```

### third_party/move/move-compiler-v2/tests/file-format-generator/bug_17602.exp
```diff
@@ -0,0 +1,30 @@
+
+============ disassembled file-format ==================
+// Move bytecode v8
+module 42.test {
+struct T<A, B> has drop {
+	x: A,
+	y: B
+}
+struct S<A, B, C> has drop {
+	_0: A,
+	_1: B,
+	_2: C
+}
+
+test_proj_0(): u8 /* def_idx: 0 */ {
+L0:	x: u8
+B0:
+	0: LdU8(42)
+	1: LdConst[0](Address: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
+	2: LdTrue
+	3: PackGeneric[0](S<u8, address, bool>)
+	4: UnpackGeneric[0](S<u8, address, bool>)
+	5: Pop
+	6: Pop
+	7: StLoc[0](x: u8)
+	8: MoveLoc[0](x: u8)
+	9: Ret
+}
+}
+============ bytecode verification succeeded ========
```

### third_party/move/move-compiler-v2/tests/file-format-generator/bug_17602.move
```diff
@@ -0,0 +1,18 @@
+module 0x42::test {
+	struct S<A, B, C>(A, B, C) has drop;
+
+	struct T<A, B> has drop {
+		x: A,
+		y: B
+	}
+
+	inline fun proj_0<A, B: drop, C: drop>(self: S<A, B, C>): A {
+		let S(x, ..) = self;
+		x
+	}
+
+	fun test_proj_0(): u8 {
+		let x = S(42, @0x1, true);
+		x.proj_0()
+	}
+}
```

### third_party/move/move-compiler-v2/tests/file-format-generator/bug_17602.opt.exp
```diff
@@ -0,0 +1,27 @@
+
+============ disassembled file-format ==================
+// Move bytecode v8
+module 42.test {
+struct T<A, B> has drop {
+	x: A,
+	y: B
+}
+struct S<A, B, C> has drop {
+	_0: A,
+	_1: B,
+	_2: C
+}
+
+test_proj_0(): u8 /* def_idx: 0 */ {
+B0:
+	0: LdU8(42)
+	1: LdConst[0](Address: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
+	2: LdTrue
+	3: PackGeneric[0](S<u8, address, bool>)
+	4: UnpackGeneric[0](S<u8, address, bool>)
+	5: Pop
+	6: Pop
+	7: Ret
+}
+}
+============ bytecode verification succeeded ========
```

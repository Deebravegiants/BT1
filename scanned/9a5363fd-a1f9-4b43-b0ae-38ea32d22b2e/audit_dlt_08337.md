# [?] Coverage crash fix. (#15857)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2025-02-04
Source: https://github.com/aptos-labs/aptos-core/commit/b829db1b2ff6e38c09acfc4d8d285582ee601fcb
Type: security-commit

## Details
Coverage crash fix. (#15857)

## Patch
### crates/aptos/src/move_tool/bytecode.rs
```diff
@@ -34,7 +34,7 @@ use move_model::metadata::{CompilationMetadata, CompilerVersion, LanguageVersion
 use serde::{Deserialize, Serialize};
 use std::{
     fs,
-    path::{Path, PathBuf},
+    path::{Component, Path, PathBuf},
     process::Command,
     str,
 };
@@ -267,11 +267,43 @@ impl BytecodeCommand {
 
     fn disassemble(&self, bytecode_path: &Path) -> Result<String, CliError> {
         let bytecode_bytes = read_from_file(bytecode_path)?;
-        let move_path = bytecode_path.with_extension(MOVE_EXTENSION);
-        let source_map_path = bytecode_path.with_extension(SOURCE_MAP_EXTENSION);
 
-        let source = fs::read_to_string(move_path).ok();
-        let source_map = source_map_from_file(&source_map_path).ok();
+        let source = {
+            let move_path = bytecode_path.with_extension(MOVE_EXTENSION);
+            if let Ok(source) = fs::read_to_string(move_path.clone()) {
+                Some(source)
+            } else {
+                let move_path = move_path
+                    .components()
+                    .map(|elt| {
+                        if elt.as_os_str() == "bytecode_modules" {
+                            Component::Normal("sources".as_ref())
+                        } else {
+                            elt
+                        }
+                    })
+                    .collect::<PathBuf>();
+                fs::read_to_string(move_path).ok()
+            }
+        };
+        let source_map = {
+            let source_map_path = bytecode_path.with_extension(SOURCE_MAP_EXTENSION);
+            if let Ok(source_map) = source_map_from_file(&source_map_path) {
+                Some(source_map)
+            } else {
+                let source_map_path = source_map_path
+                    .components()
+                    .map(|elt| {
+                        if elt.as_os_str() == "bytecode_modules" {
+                            Component::Normal("source_maps".as_ref())
+                        } else {
+                            elt
+                        }
+                    })
+                    .collect::<PathBuf>();
+                source_map_from_file(&source_map_path).ok()
+            }
+        };
 
         let disassembler_options = DisassemblerOptions {
             print_code: true,
```

### crates/aptos/src/move_tool/coverage.rs
```diff
@@ -119,13 +119,20 @@ impl CliCommand<()> for SourceCoverage {
         let (coverage_map, package) = compile_coverage(self.move_options)?;
         let unit = package.get_module_by_name_from_root(&self.module_name)?;
         let source_path = &unit.source_path;
-        let (module, source_map) = match &unit.unit {
-            CompiledUnit::Module(NamedCompiledModule {
-                module, source_map, ..
-            }) => (module, source_map),
+        let source_map = match &unit.unit {
+            CompiledUnit::Module(NamedCompiledModule { source_map, .. }) => source_map,
             _ => panic!("Should all be modules"),
         };
-        let source_coverage = SourceCoverageBuilder::new(module, &coverage_map, source_map);
+        let root_modules: Vec<_> = package
+            .root_modules()
+            .map(|unit| match &unit.unit {
+                CompiledUnit::Module(NamedCompiledModule {
+                    module, source_map, ..
+                }) => (module, source_map),
+                _ => unreachable!("Should all be modules"),
+            })
+            .collect();
+        let source_coverage = SourceCoverageBuilder::new(&coverage_map, source_map, root_modules);
         let source_coverage = source_coverage.compute_source_coverage(source_path);
         let output_result =
             source_coverage.output_source_coverage(&mut std::io::stdout(), self.color, self.tag);
@@ -189,7 +196,7 @@ fn compile_coverage(
 
     let path = move_options.get_package_path()?;
     let coverage_map =
-        CoverageMap::from_binary_file(path.join(".coverage_map.mvcov")).map_err(|err| {
+        CoverageMap::from_binary_file(&path.join(".coverage_map.mvcov")).map_err(|err| {
             CliError::UnexpectedError(format!("Failed to retrieve coverage map {}", err))
         })?;
     let package = config
```

### third_party/move/move-compiler-v2/src/lib.rs
```diff
@@ -48,9 +48,8 @@ use codespan_reporting::{
 };
 pub use experiments::{Experiment, EXPERIMENTS};
 use log::{debug, info, log_enabled, Level};
-use move_binary_format::{binary_views::BinaryIndexedView, errors::VMError};
+use move_binary_format::errors::VMError;
 use move_bytecode_source_map::source_map::SourceMap;
-use move_command_line_common::files::FileHash;
 use move_compiler::{
     command_line,
     compiled_unit::{
@@ -62,7 +61,6 @@ use move_compiler::{
 };
 use move_core_types::vm_status::StatusType;
 use move_disassembler::disassembler::Disassembler;
-use move_ir_types::location;
 use move_model::{
     metadata::LanguageVersion,
     model::{GlobalEnv, Loc, MoveIrLoc},
@@ -515,14 +513,7 @@ pub fn bytecode_pipeline(env: &GlobalEnv) -> FunctionTargetPipeline {
 pub fn disassemble_compiled_units(units: &[CompiledUnit]) -> anyhow::Result<String> {
     let disassembled_units: anyhow::Result<Vec<_>> = units
         .iter()
-        .map(|unit| {
-            let view = match unit {
-                CompiledUnit::Module(module) => BinaryIndexedView::Module(&module.module),
-                CompiledUnit::Script(script) => BinaryIndexedView::Script(&script.script),
-            };
-            Disassembler::from_view(view, location::Loc::new(FileHash::empty(), 0, 0))
-                .and_then(|d| d.disassemble())
-        })
+        .map(|unit| Disassembler::from_unit(unit).disassemble())
         .collect();
     Ok(disassembled_units?.concat())
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/borrowed_from_one_path.exp
```diff
@@ -678,29 +678,29 @@ struct R has key {
 	data: vector<u64>
 }
 
-f(Arg0: u8, Arg1: &vector<u64>): u64 /* def_idx: 0 */ {
-L2:	loc0: &vector<u64>
+f(k: u8, d: &vector<u64>): u64 /* def_idx: 0 */ {
+L2:	v: &vector<u64>
 B0:
-	0: MoveLoc[0](Arg0: u8)
+	0: MoveLoc[0](k: u8)
 	1: LdU8(0)
 	2: Eq
 	3: BrFalse(15)
 B1:
-	4: MoveLoc[1](Arg1: &vector<u64>)
+	4: MoveLoc[1](d: &vector<u64>)
 	5: Pop
 	6: LdConst[0](Address: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
 	7: ImmBorrowGlobal[0](R)
 	8: ImmBorrowField[0](R.data: vector<u64>)
-	9: StLoc[2](loc0: &vector<u64>)
+	9: StLoc[2](v: &vector<u64>)
 B2:
-	10: MoveLoc[2](loc0: &vector<u64>)
+	10: MoveLoc[2](v: &vector<u64>)
 	11: LdU64(0)
 	12: VecImmBorrow(1)
 	13: ReadRef
 	14: Ret
 B3:
-	15: MoveLoc[1](Arg1: &vector<u64>)
-	16: StLoc[2](loc0: &vector<u64>)
+	15: MoveLoc[1](d: &vector<u64>)
+	16: StLoc[2](v: &vector<u64>)
 	17: Branch(10)
 }
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/by_reference.exp
```diff
@@ -2247,10 +2247,10 @@ script {
 
 
 main() /* def_idx: 0 */ {
-L0:	loc0: u64
-L1:	loc1: &mut u64
-L2:	loc2: vector<u8>
-L3:	loc3: &mut vector<u8>
+L0:	$t13: u64
+L1:	c: &mut u64
+L2:	$t16: vector<u8>
+L3:	b: &mut vector<u8>
 B0:
 	0: LdU64(0)
 	1: LdU64(0)
@@ -2263,26 +2263,26 @@ B1:
 	7: BrFalse(43)
 B2:
 	8: LdU64(0)
-	9: StLoc[0](loc0: u64)
-	10: MutBorrowLoc[0](loc0: u64)
-	11: StLoc[1](loc1: &mut u64)
+	9: StLoc[0]($t13: u64)
+	10: MutBorrowLoc[0]($t13: u64)
+	11: StLoc[1](c: &mut u64)
 	12: LdU64(1)
-	13: CopyLoc[1](loc1: &mut u64)
+	13: CopyLoc[1](c: &mut u64)
 	14: WriteRef
 	15: LdConst[0](Vector(U8): [5, 104, 101, 108, 108, 111])
-	16: StLoc[2](loc2: vector<u8>)
-	17: MutBorrowLoc[2](loc2: vector<u8>)
-	18: StLoc[3](loc3: &mut vector<u8>)
+	16: StLoc[2]($t16: vector<u8>)
+	17: MutBorrowLoc[2]($t16: vector<u8>)
+	18: StLoc[3](b: &mut vector<u8>)
 	19: LdConst[1](Vector(U8): [3, 98, 121, 101])
-	20: CopyLoc[3](loc3: &mut vector<u8>)
+	20: CopyLoc[3](b: &mut vector<u8>)
 	21: WriteRef
-	22: MoveLoc[1](loc1: &mut u64)
+	22: MoveLoc[1](c: &mut u64)
 	23: ReadRef
 	24: LdU64(1)
 	25: Eq
 	26: BrFalse(39)
 B3:
-	27: MoveLoc[3](loc3: &mut vector<u8>)
+	27: MoveLoc[3](b: &mut vector<u8>)
 	28: ReadRef
 	29: LdConst[1](Vector(U8): [3, 98, 121, 101])
 	30: Eq
@@ -2299,7 +2299,7 @@ B7:
 	37: LdU64(42)
 	38: Abort
 B8:
-	39: MoveLoc[3](loc3: &mut vector<u8>)
+	39: MoveLoc[3](b: &mut vector<u8>)
 	40: Pop
 	41: LdU64(42)
 	42: Abort
```

### third_party/move/move-compiler-v2/tests/ability-transform/copy_ability_tuple.exp
```diff
@@ -448,22 +448,22 @@ struct R has key {
 	f: u64
 }
 
-public f(Arg0: R): R * u64 /* def_idx: 0 */ {
+public f(r: R): R * u64 /* def_idx: 0 */ {
 B0:
-	0: MoveLoc[0](Arg0: R)
+	0: MoveLoc[0](r: R)
 	1: LdU64(0)
 	2: Ret
 }
-public g(Arg0: &signer) /* def_idx: 1 */ {
-L1:	loc0: R
+public g(s: &signer) /* def_idx: 1 */ {
+L1:	r: R
 B0:
 	0: LdU64(1)
 	1: Pack[0](R)
 	2: Call f(R): R * u64
 	3: Pop
-	4: StLoc[1](loc0: R)
-	5: MoveLoc[0](Arg0: &signer)
-	6: MoveLoc[1](loc0: R)
+	4: StLoc[1](r: R)
+	5: MoveLoc[0](s: &signer)
+	6: MoveLoc[1](r: R)
 	7: MoveTo[0](R)
 	8: Ret
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/dead_but_borrowed.exp
```diff
@@ -195,11 +195,11 @@ module 42.explicate_drop {
 
 
 test0(): u8 /* def_idx: 0 */ {
-L0:	loc0: u8
+L0:	$t2: u8
 B0:
 	0: LdU8(42)
-	1: StLoc[0](loc0: u8)
-	2: ImmBorrowLoc[0](loc0: u8)
+	1: StLoc[0]($t2: u8)
+	2: ImmBorrowLoc[0]($t2: u8)
 	3: ReadRef
 	4: Ret
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/destroy_after_call.exp
```diff
@@ -404,22 +404,22 @@ fun m::g() {
 module 42.m {
 
 
-f(Arg0: &mut u64): &mut u64 /* def_idx: 0 */ {
+f(r: &mut u64): &mut u64 /* def_idx: 0 */ {
 B0:
-	0: MoveLoc[0](Arg0: &mut u64)
+	0: MoveLoc[0](r: &mut u64)
 	1: Ret
 }
 g() /* def_idx: 1 */ {
-L0:	loc0: u64
-L1:	loc1: &mut u64
-L2:	loc2: &u64
+L0:	v: u64
+L1:	r: &mut u64
+L2:	_r: &u64
 B0:
 	0: LdU64(22)
-	1: StLoc[0](loc0: u64)
-	2: MutBorrowLoc[0](loc0: u64)
+	1: StLoc[0](v: u64)
+	2: MutBorrowLoc[0](v: u64)
 	3: Call f(&mut u64): &mut u64
 	4: Pop
-	5: ImmBorrowLoc[0](loc0: u64)
+	5: ImmBorrowLoc[0](v: u64)
 	6: Pop
 	7: Ret
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/drop_after_loop.exp
```diff
@@ -833,30 +833,30 @@ module 42.m {
 
 
 drop_after_loop() /* def_idx: 0 */ {
-L0:	loc0: u64
-L1:	loc1: &mut u64
-L2:	loc2: bool
+L0:	l: u64
+L1:	r: &mut u64
+L2:	c: bool
 B0:
 	0: LdU64(1)
-	1: StLoc[0](loc0: u64)
-	2: MutBorrowLoc[0](loc0: u64)
-	3: StLoc[1](loc1: &mut u64)
+	1: StLoc[0](l: u64)
+	2: MutBorrowLoc[0](l: u64)
+	3: StLoc[1](r: &mut u64)
 	4: LdTrue
-	5: StLoc[2](loc2: bool)
+	5: StLoc[2](c: bool)
 B1:
-	6: MoveLoc[2](loc2: bool)
+	6: MoveLoc[2](c: bool)
 	7: BrFalse(14)
 B2:
 	8: LdU64(2)
-	9: CopyLoc[1](loc1: &mut u64)
+	9: CopyLoc[1](r: &mut u64)
 	10: WriteRef
 	11: LdFalse
-	12: StLoc[2](loc2: bool)
+	12: StLoc[2](c: bool)
 	13: Branch(6)
 B3:
-	14: MoveLoc[1](loc1: &mut u64)
+	14: MoveLoc[1](r: &mut u64)
 	15: Pop
-	16: MoveLoc[0](loc0: u64)
+	16: MoveLoc[0](l: u64)
 	17: LdU64(2)
 	18: Eq
 	19: BrFalse(21)
```

### third_party/move/move-compiler-v2/tests/ability-transform/drop_at_branch.exp
```diff
@@ -258,20 +258,20 @@ fun explicate_drop::drop_at_branch($t0: bool): u8 {
 module 42.explicate_drop {
 
 
-drop_at_branch(Arg0: bool): u8 /* def_idx: 0 */ {
-L1:	loc0: u8
+drop_at_branch(x: bool): u8 /* def_idx: 0 */ {
+L1:	return: u8
 B0:
-	0: MoveLoc[0](Arg0: bool)
+	0: MoveLoc[0](x: bool)
 	1: BrFalse(6)
 B1:
 	2: LdU8(1)
-	3: StLoc[1](loc0: u8)
+	3: StLoc[1](return: u8)
 B2:
-	4: MoveLoc[1](loc0: u8)
+	4: MoveLoc[1](return: u8)
 	5: Ret
 B3:
 	6: LdU8(0)
-	7: StLoc[1](loc0: u8)
+	7: StLoc[1](return: u8)
 	8: Branch(4)
 }
 }
```

### third_party/move/move-compiler-v2/tests/ability-transform/foreach_mut_expanded.exp
```diff
@@ -1157,44 +1157,44 @@ module 42.m {
 
 
 test_for_each_mut() /* def_idx: 0 */ {
-L0:	loc0: vector<u64>
-L1:	loc1: u64
-L2:	loc2: u64
-L3:	loc3: &mut vector<u64>
-L4:	loc4: u64
-L5:	loc5: &mut u64
+L0:	v: vector<u64>
+L1:	i: u64
+L2:	len: u64
+L3:	vr: &mut vector<u64>
+L4:	$t6: u64
+L5:	x: &mut u64
 B0:
 	0: LdConst[0](Vector(U64): [3, 1, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0])
-	1: StLoc[0](loc0: vector<u64>)
+	1: StLoc[0](v: vector<u64>)
 	2: LdU64(0)
-	3: StLoc[1](loc1: u64)
-	4: ImmBorrowLoc[0](loc0: vector<u64>)
+	3: StLoc[1](i: u64)
+	4: ImmBorrowLoc[0](v: vector<u64>)
 	5: VecLen(1)
-	6: StLoc[2](loc2: u64)
-	7: MutBorrowLoc[0](loc0: vector<u64>)
-	8: StLoc[3](loc3: &mut vector<u64>)
+	6: StLoc[2](len: u64)
+	7: MutBorrowLoc[0](v: vector<u64>)
+	8: StLoc[3](vr: &mut vector<u64>)
 B1:
-	9: CopyLoc[1](loc1: u64)
-	10: CopyLoc[2](loc2: u64)
+	9: CopyLoc[1](i: u64)
+	10: CopyLoc[2](len: u64)
 	11: Lt
 	12: BrFalse(25)
 B2:
-	13: CopyLoc[3](loc3: &mut vector<u64>)
-	14: CopyLoc[1](loc1: u64)
+	13: CopyLoc[3](vr: &mut vector<u64>)
+	14: CopyLoc[1](i: u64)
 	15: VecMutBorrow(1)
-	16: StLoc[5](loc5: &mut u64)
+	16: StLoc[5](x: &mut u64)
 	17: LdU64(2)
-	18: MoveLoc[5](loc5: &mut u64)
+	18: MoveLoc[5](x: &mut u64)
 	19: WriteRef
-	20: MoveLoc[1](loc1: u64)
+	20: MoveLoc[1](i: u64)
 	21: LdU64(1)
 	22: Add
-	23: StLoc[1](loc1: u64)
+	23: StLoc[1](i: u64)
 	24: Branch(9)
 B3:
-	25: MoveLoc[3](loc3: &mut vector<u64>)
+	25: MoveLoc[3](vr: &mut vector<u64>)
 	26: Pop
-	27: MoveLoc[0](loc0: vector<u64>)
+	27: MoveLoc[0](v: vector<u64>)
 	28: LdConst[1](Vector(U64): [3, 2, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0])
 	29: Eq
 	30: BrFalse(32)
```

### third_party/move/move-compiler-v2/tests/ability-transform/mutate_return.exp
```diff
@@ -307,20 +307,20 @@ fun m::g<#0>($t0: &mut vector<#0>) {
 module c0ffee.m {
 
 
-public singleton<Ty0>(Arg0: Ty0): vector<Ty0> /* def_idx: 0 */ {
-L1:	loc0: vector<Ty0>
+public singleton<Element>(e: Element): vector<Element> /* def_idx: 0 */ {
+L1:	v: vector<Element>
 B0:
-	0: MoveLoc[0](Arg0: Ty0)
+	0: MoveLoc[0](e: Element)
 	1: VecPack(0, 1)
-	2: StLoc[1](loc0: vector<Ty0>)
-	3: MutBorrowLoc[1](loc0: vector<Ty0>)
-	4: Call g<Ty0>(&mut vector<Ty0>)
-	5: MoveLoc[1](loc0: vector<Ty0>)
+	2: StLoc[1](v: vector<Element>)
+	3: MutBorrowLoc[1](v: vector<Element>)
+	4: Call g<Element>(&mut vector<Element>)
+	5: MoveLoc[1](v: vector<Element>)
 	6: Ret
 }
-g<Ty0>(Arg0: &mut vector<Ty0>) /* def_idx: 1 */ {
+g<A>(_v: &mut vector<A>) /* def_idx: 1 */ {
 B0:
-	0: MoveLoc[0](Arg0: &mut vector<Ty0>)
+	0: MoveLoc[0](_v: &mut vector<A>)
 	1: Pop
 	2: Ret
 }
```

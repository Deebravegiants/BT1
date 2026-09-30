# [?] Fix the bug that move-disassembler panicked for using wrong type_param_context when handling generic types (#49)

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2022-04-18
Source: https://github.com/move-language/move/commit/5d600b7067f29f9e224982f16cad3899407816fa
Type: security-commit

## Details
Fix the bug that move-disassembler panicked for using wrong type_param_context when handling generic types (#49)

## Patch
### language/tools/move-disassembler/src/disassembler.rs
```diff
@@ -265,18 +265,13 @@ impl<'a> Disassembler<'a> {
         &self,
         struct_idx: StructDefinitionIndex,
         signature: &Signature,
+        type_param_context: &[SourceName],
     ) -> Result<(String, String)> {
         let struct_definition = self.get_struct_def(struct_idx)?;
-        let struct_source_map = self
-            .source_mapper
-            .source_map
-            .get_struct_source_map(struct_idx)?;
         let type_arguments = signature
             .0
             .iter()
-            .map(|sig_tok| {
-                self.disassemble_sig_tok(sig_tok.clone(), &struct_source_map.type_parameters)
-            })
+            .map(|sig_tok| self.disassemble_sig_tok(sig_tok.clone(), type_param_context))
             .collect::<Result<Vec<String>>>()?;
 
         let struct_handle = self
@@ -554,7 +549,11 @@ impl<'a> Disassembler<'a> {
                 ))
             }
             Bytecode::Pack(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!("Pack[{}]({}{})", struct_idx, name, ty_params))
             }
             Bytecode::PackGeneric(struct_idx) => {
@@ -566,14 +565,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "PackGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::Unpack(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!("Unpack[{}]({}{})", struct_idx, name, ty_params))
             }
             Bytecode::UnpackGeneric(struct_idx) => {
@@ -585,14 +592,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "UnpackGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::Exists(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!("Exists[{}]({}{})", struct_idx, name, ty_params))
             }
             Bytecode::ExistsGeneric(struct_idx) => {
@@ -604,14 +619,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "ExistsGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::MutBorrowGlobal(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "MutBorrowGlobal[{}]({}{})",
                     struct_idx, name, ty_params
@@ -626,14 +649,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "MutBorrowGlobalGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::ImmBorrowGlobal(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "ImmBorrowGlobal[{}]({}{})",
                     struct_idx, name, ty_params
@@ -648,14 +679,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "ImmBorrowGlobalGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::MoveFrom(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!("MoveFrom[{}]({}{})", struct_idx, name, ty_params))
             }
             Bytecode::MoveFromGeneric(struct_idx) => {
@@ -667,14 +706,22 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "MoveFromGeneric[{}]({}{})",
                     struct_idx, name, ty_params
                 ))
             }
             Bytecode::MoveTo(struct_idx) => {
-                let (name, ty_params) = self.struct_type_info(*struct_idx, &Signature(vec![]))?;
+                let (name, ty_params) = self.struct_type_info(
+                    *struct_idx,
+                    &Signature(vec![]),
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!("MoveTo[{}]({}{})", struct_idx, name, ty_params))
             }
             Bytecode::MoveToGeneric(struct_idx) => {
@@ -686,7 +733,11 @@ impl<'a> Disassembler<'a> {
                     .source_mapper
                     .bytecode
                     .signature_at(struct_inst.type_parameters);
-                let (name, ty_params) = self.struct_type_info(struct_inst.def, type_params)?;
+                let (name, ty_params) = self.struct_type_info(
+                    struct_inst.def,
+                    type_params,
+                    &function_source_map.type_parameters,
+                )?;
                 Ok(format!(
                     "MoveToGeneric[{}]({}{})",
                     struct_idx, name, ty_params
```

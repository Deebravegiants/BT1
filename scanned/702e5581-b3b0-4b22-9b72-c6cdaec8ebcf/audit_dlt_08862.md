# [?] LS: fix diagnostics' panics (#6529)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/cairo
Published: 2024-10-29
Source: https://github.com/starkware-libs/cairo/commit/848b90f26c84a108c344adcbf88de07c4e8f71d4
Type: security-commit

## Details
LS: fix diagnostics' panics (#6529)

## Patch
### crates/cairo-lang-compiler/src/db.rs
```diff
@@ -1,7 +1,7 @@
 use std::sync::Arc;
 
 use anyhow::{Result, anyhow, bail};
-use cairo_lang_defs::db::{DefsDatabase, DefsGroup, ext_as_virtual_impl};
+use cairo_lang_defs::db::{DefsDatabase, DefsGroup, try_ext_as_virtual_impl};
 use cairo_lang_defs::plugin::{InlineMacroExprPlugin, MacroPlugin};
 use cairo_lang_filesystem::cfg::CfgSet;
 use cairo_lang_filesystem::db::{
@@ -39,8 +39,8 @@ pub struct RootDatabase {
 }
 impl salsa::Database for RootDatabase {}
 impl ExternalFiles for RootDatabase {
-    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
-        ext_as_virtual_impl(self.upcast(), external_id)
+    fn try_ext_as_virtual(&self, external_id: salsa::InternId) -> Option<VirtualFile> {
+        try_ext_as_virtual_impl(self.upcast(), external_id)
     }
 }
 impl salsa::ParallelDatabase for RootDatabase {
```

### crates/cairo-lang-defs/src/db.rs
```diff
@@ -576,13 +576,16 @@ fn priv_module_data(db: &dyn DefsGroup, module_id: ModuleId) -> Maybe<ModuleData
 }
 
 /// Returns the `VirtualFile` matching the given external id.
-pub fn ext_as_virtual_impl(db: &dyn DefsGroup, external_id: salsa::InternId) -> VirtualFile {
+pub fn try_ext_as_virtual_impl(
+    db: &dyn DefsGroup,
+    external_id: salsa::InternId,
+) -> Option<VirtualFile> {
     let long_id = PluginGeneratedFileId::from_intern_id(external_id).lookup_intern(db);
     let file_id = FileLongId::External(external_id).intern(db);
     let data = db
         .priv_module_sub_files(long_id.module_id, long_id.stable_ptr.file_id(db.upcast()))
         .unwrap();
-    data.files[&file_id].clone()
+    data.files.get(&file_id).cloned()
 }
 
 fn priv_module_sub_files(
```

### crates/cairo-lang-defs/src/test.rs
```diff
@@ -17,7 +17,7 @@ use cairo_lang_utils::ordered_hash_map::OrderedHashMap;
 use cairo_lang_utils::{Intern, LookupIntern, Upcast, extract_matches, try_extract_matches};
 use indoc::indoc;
 
-use crate::db::{DefsDatabase, DefsGroup, ext_as_virtual_impl};
+use crate::db::{DefsDatabase, DefsGroup, try_ext_as_virtual_impl};
 use crate::ids::{
     FileIndex, GenericParamLongId, ModuleFileId, ModuleId, ModuleItemId, NamedLanguageElementId,
     SubmoduleLongId,
@@ -32,8 +32,8 @@ pub struct DatabaseForTesting {
 }
 impl salsa::Database for DatabaseForTesting {}
 impl ExternalFiles for DatabaseForTesting {
-    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
-        ext_as_virtual_impl(self.upcast(), external_id)
+    fn try_ext_as_virtual(&self, external_id: salsa::InternId) -> Option<VirtualFile> {
+        try_ext_as_virtual_impl(self.upcast(), external_id)
     }
 }
 impl Default for DatabaseForTesting {
```

### crates/cairo-lang-filesystem/src/db.rs
```diff
@@ -161,7 +161,12 @@ pub struct ExperimentalFeaturesConfig {
 /// A trait for defining files external to the `filesystem` crate.
 pub trait ExternalFiles {
     /// Returns the virtual file matching the external id.
-    fn ext_as_virtual(&self, _external_id: salsa::InternId) -> VirtualFile {
+    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
+        self.try_ext_as_virtual(external_id).unwrap()
+    }
+
+    /// Returns the virtual file matching the external id if found.
+    fn try_ext_as_virtual(&self, _external_id: salsa::InternId) -> Option<VirtualFile> {
         panic!("Should not be called, unless specifically implemented!");
     }
 }
```

### crates/cairo-lang-language-server/src/ide/navigation/goto_definition.rs
```diff
@@ -16,7 +16,7 @@ pub fn goto_definition(
     let file = db.file_for_url(&params.text_document_position_params.text_document.uri)?;
     let position = params.text_document_position_params.position.to_cairo();
     let (found_file, span) = get_definition_location(db, file, position)?;
-    let found_uri = db.url_for_file(found_file);
+    let found_uri = db.url_for_file(found_file)?;
 
     let range = span.position_in_file(db.upcast(), found_file)?.to_lsp();
     Some(GotoDefinitionResponse::Scalar(Location { uri: found_uri, range }))
```

### crates/cairo-lang-language-server/src/lang/db/mod.rs
```diff
@@ -1,4 +1,4 @@
-use cairo_lang_defs::db::{DefsDatabase, DefsGroup, ext_as_virtual_impl};
+use cairo_lang_defs::db::{DefsDatabase, DefsGroup, try_ext_as_virtual_impl};
 use cairo_lang_doc::db::DocDatabase;
 use cairo_lang_filesystem::cfg::{Cfg, CfgSet};
 use cairo_lang_filesystem::db::{
@@ -87,8 +87,8 @@ impl AnalysisDatabase {
 
 impl salsa::Database for AnalysisDatabase {}
 impl ExternalFiles for AnalysisDatabase {
-    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
-        ext_as_virtual_impl(self.upcast(), external_id)
+    fn try_ext_as_virtual(&self, external_id: salsa::InternId) -> Option<VirtualFile> {
+        try_ext_as_virtual_impl(self.upcast(), external_id)
     }
 }
 
```

### crates/cairo-lang-language-server/src/lang/diagnostics/lsp.rs
```diff
@@ -1,11 +1,11 @@
 use cairo_lang_diagnostics::{DiagnosticEntry, DiagnosticLocation, Diagnostics, Severity};
 use cairo_lang_filesystem::db::FilesGroup;
 use cairo_lang_filesystem::ids::FileId;
-use cairo_lang_utils::Upcast;
+use cairo_lang_utils::{LookupIntern, Upcast};
 use lsp_types::{
     Diagnostic, DiagnosticRelatedInformation, DiagnosticSeverity, Location, NumberOrString, Range,
 };
-use tracing::error;
+use tracing::{error, trace};
 
 use crate::lang::lsp::{LsProtoGroup, ToLsp};
 
@@ -34,8 +34,12 @@ pub fn map_cairo_diagnostics_to_lsp<T: DiagnosticEntry>(
                 ) else {
                     continue;
                 };
+                let Some(uri) = db.url_for_file(file_id) else {
+                    trace!("url for file not found: {:?}", file_id.lookup_intern(db));
+                    continue;
+                };
                 related_information.push(DiagnosticRelatedInformation {
-                    location: Location { uri: db.url_for_file(file_id), range },
+                    location: Location { uri, range },
                     message: note.text.clone(),
                 });
             } else {
@@ -83,7 +87,7 @@ fn get_mapped_range_and_add_mapping_note(
         if *orig != mapped {
             if let Some(range) = get_lsp_range(db.upcast(), orig) {
                 related_info.push(DiagnosticRelatedInformation {
-                    location: Location { uri: db.url_for_file(orig.file_id), range },
+                    location: Location { uri: db.url_for_file(orig.file_id)?, range },
                     message: message.to_string(),
                 });
             }
```

### crates/cairo-lang-language-server/src/lang/diagnostics/refresh.rs
```diff
@@ -11,10 +11,10 @@ use cairo_lang_lowering::diagnostic::LoweringDiagnostic;
 use cairo_lang_parser::db::ParserGroup;
 use cairo_lang_semantic::SemanticDiagnostic;
 use cairo_lang_semantic::db::SemanticGroup;
-use cairo_lang_utils::Upcast;
+use cairo_lang_utils::{LookupIntern, Upcast};
 use lsp_types::notification::PublishDiagnostics;
 use lsp_types::{PublishDiagnosticsParams, Url};
-use tracing::{error, info_span};
+use tracing::{error, info_span, trace};
 
 use crate::lang::db::AnalysisDatabase;
 use crate::lang::diagnostics::lsp::map_cairo_diagnostics_to_lsp;
@@ -123,7 +123,11 @@ fn refresh_file_diagnostics(
     file_diagnostics: &mut HashMap<Url, FileDiagnostics>,
     notifier: &Notifier,
 ) {
-    let file_uri = db.url_for_file(*file);
+    let Some(file_uri) = db.url_for_file(*file) else {
+        trace!("url for file not found: {:?}", file.lookup_intern(db));
+        return;
+    };
+
     let mut semantic_file_diagnostics: Vec<SemanticDiagnostic> = vec![];
     let mut lowering_file_diagnostics: Vec<LoweringDiagnostic> = vec![];
 
```

### crates/cairo-lang-language-server/src/lang/lsp/ls_proto_group.rs
```diff
@@ -41,18 +41,18 @@ pub trait LsProtoGroup: Upcast<dyn FilesGroup> {
     }
 
     /// Get the canonical [`Url`] for a [`FileId`].
-    fn url_for_file(&self, file_id: FileId) -> Url {
+    fn url_for_file(&self, file_id: FileId) -> Option<Url> {
         let vf = match self.upcast().lookup_intern_file(file_id) {
-            FileLongId::OnDisk(path) => return Url::from_file_path(path).unwrap(),
+            FileLongId::OnDisk(path) => return Some(Url::from_file_path(path).unwrap()),
             FileLongId::Virtual(vf) => vf,
-            FileLongId::External(id) => self.upcast().ext_as_virtual(id),
+            FileLongId::External(id) => self.upcast().try_ext_as_virtual(id)?,
         };
         // NOTE: The URL is constructed using setters and path segments in order to
         //   url-encode any funky characters in parts that LS is not controlling.
         let mut url = Url::parse("vfs://").unwrap();
         url.set_host(Some(&file_id.as_intern_id().to_string())).unwrap();
         url.path_segments_mut().unwrap().push(&format!("{}.cairo", vf.name));
-        url
+        Some(url)
     }
 }
 
```

### crates/cairo-lang-language-server/src/lang/lsp/ls_proto_group_test.rs
```diff
@@ -14,7 +14,7 @@ fn file_url() {
         let expected_file = db.intern_file(expected_file_long);
 
         assert_eq!(db.file_for_url(&expected_url), Some(expected_file));
-        assert_eq!(db.url_for_file(expected_file), expected_url);
+        assert_eq!(db.url_for_file(expected_file), Some(expected_url));
     };
 
     check("file:///foo/bar", FileLongId::OnDisk("/foo/bar".into()));
```

### crates/cairo-lang-lowering/src/test_utils.rs
```diff
@@ -1,6 +1,6 @@
 use std::sync::{LazyLock, Mutex};
 
-use cairo_lang_defs::db::{DefsDatabase, DefsGroup, ext_as_virtual_impl};
+use cairo_lang_defs::db::{DefsDatabase, DefsGroup, try_ext_as_virtual_impl};
 use cairo_lang_filesystem::db::{
     AsFilesGroupMut, ExternalFiles, FilesDatabase, FilesGroup, init_dev_corelib, init_files_group,
 };
@@ -28,8 +28,8 @@ pub struct LoweringDatabaseForTesting {
 }
 impl salsa::Database for LoweringDatabaseForTesting {}
 impl ExternalFiles for LoweringDatabaseForTesting {
-    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
-        ext_as_virtual_impl(self.upcast(), external_id)
+    fn try_ext_as_virtual(&self, external_id: salsa::InternId) -> Option<VirtualFile> {
+        try_ext_as_virtual_impl(self.upcast(), external_id)
     }
 }
 impl salsa::ParallelDatabase for LoweringDatabaseForTesting {
```

### crates/cairo-lang-plugins/src/test.rs
```diff
@@ -1,6 +1,6 @@
 use std::sync::Arc;
 
-use cairo_lang_defs::db::{DefsDatabase, DefsGroup, ext_as_virtual_impl};
+use cairo_lang_defs::db::{DefsDatabase, DefsGroup, try_ext_as_virtual_impl};
 use cairo_lang_defs::ids::ModuleId;
 use cairo_lang_defs::plugin::{
     MacroPlugin, MacroPluginMetadata, PluginDiagnostic, PluginGeneratedFile, PluginResult,
@@ -52,8 +52,8 @@ pub struct DatabaseForTesting {
 }
 impl salsa::Database for DatabaseForTesting {}
 impl ExternalFiles for DatabaseForTesting {
-    fn ext_as_virtual(&self, external_id: salsa::InternId) -> VirtualFile {
-        ext_as_virtual_impl(self.upcast(), external_id)
+    fn try_ext_as_virtual(&self, external_id: salsa::InternId) -> Option<VirtualFile> {
+        try_ext_as_virtual_impl(self.upcast(), external_id)
     }
 }
 impl Default for DatabaseForTesting {
```

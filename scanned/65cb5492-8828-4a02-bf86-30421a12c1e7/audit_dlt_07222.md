# [?] [move-compiler] Fix panic in coverage for inlined code, add controls to display tags and/or color in coverage source listings, don't lean on compiler 

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-08-29
Source: https://github.com/aptos-labs/aptos-core/commit/5eb0f1deeac7ef9bfbb70888d4a7b65cb62aa700
Type: security-commit

## Details
[move-compiler] Fix panic in coverage for inlined code, add controls to display tags and/or color in coverage source listings, don't lean on compiler v1 (#14449)

- Add controls --color and --tag for showing coverage.  Fix panic by dropping inlined code from source coverage listings.
- fix aptos move test --coverage to not necessarily use compiler-v1

Fixes #14377
Fixes #14360
Fixes #14379
Fixes #14454

## Patch
### crates/aptos/src/move_tool/coverage.rs
```diff
@@ -1,14 +1,19 @@
 // Copyright © Aptos Foundation
 // SPDX-License-Identifier: Apache-2.0
 
-use crate::common::types::{CliCommand, CliError, CliResult, CliTypedResult, MovePackageDir};
+use crate::{
+    common::types::{CliCommand, CliError, CliResult, CliTypedResult, MovePackageDir},
+    move_tool::{experiments_from_opt_level, fix_bytecode_version},
+};
 use aptos_framework::extended_checks;
 use async_trait::async_trait;
 use clap::{Parser, Subcommand};
 use move_compiler::compiled_unit::{CompiledUnit, NamedCompiledModule};
 use move_coverage::{
-    coverage_map::CoverageMap, format_csv_summary, format_human_summary,
-    source_coverage::SourceCoverageBuilder, summary::summarize_inst_cov,
+    coverage_map::CoverageMap,
+    format_csv_summary, format_human_summary,
+    source_coverage::{ColorChoice, SourceCoverageBuilder, TextIndicator},
+    summary::summarize_inst_cov,
 };
 use move_disassembler::disassembler::Disassembler;
 use move_package::{compilation::compiled_package::CompiledPackage, BuildConfig, CompilerConfig};
@@ -87,8 +92,18 @@ impl CliCommand<()> for SummaryCoverage {
 /// Display coverage information about the module against source code
 #[derive(Debug, Parser)]
 pub struct SourceCoverage {
+    /// Show coverage for the given module
     #[clap(long = "module")]
     pub module_name: String,
+
+    /// Colorize output based on coverage
+    #[clap(long, default_value_t = ColorChoice::Default)]
+    pub color: ColorChoice,
+
+    /// Tag each line with a textual indication of coverage
+    #[clap(long, default_value_t = TextIndicator::Explicit)]
+    pub tag: TextIndicator,
+
     #[clap(flatten)]
     pub move_options: MovePackageDir,
 }
@@ -110,9 +125,10 @@ impl CliCommand<()> for SourceCoverage {
             _ => panic!("Should all be modules"),
         };
         let source_coverage = SourceCoverageBuilder::new(module, &coverage_map, source_map);
-        source_coverage
-            .compute_source_coverage(source_path)
-            .output_source_coverage(&mut std::io::stdout())
+        let source_coverage = source_coverage.compute_source_coverage(source_path);
+        let output_result =
+            source_coverage.output_source_coverage(&mut std::io::stdout(), self.color, self.tag);
+        output_result
             .map_err(|err| CliError::UnexpectedError(format!("Failed to get coverage {}", err)))
     }
 }
@@ -149,14 +165,23 @@ fn compile_coverage(
         dev_mode: move_options.dev,
         additional_named_addresses: move_options.named_addresses(),
         test_mode: false,
+        full_model_generation: move_options.check_test_code,
         install_dir: move_options.output_dir.clone(),
+        skip_fetch_latest_git_deps: move_options.skip_fetch_latest_git_deps,
         compiler_config: CompilerConfig {
             known_attributes: extended_checks::get_all_attribute_names().clone(),
-            skip_attribute_checks: false,
-            ..Default::default()
+            skip_attribute_checks: move_options.skip_attribute_checks,
+            bytecode_version: fix_bytecode_version(
+                move_options.bytecode_version,
+                move_options.language_version,
+            ),
+            compiler_version: move_options.compiler_version,
+            language_version: move_options.language_version,
+            experiments: experiments_from_opt_level(&move_options.optimize),
         },
         ..Default::default()
     };
+
     let path = move_options.get_package_path()?;
     let coverage_map =
         CoverageMap::from_binary_file(path.join(".coverage_map.mvcov")).map_err(|err| {
```

### crates/aptos/src/move_tool/mod.rs
```diff
@@ -506,7 +506,7 @@ pub struct TestPackage {
     pub dump_state: bool,
 }
 
-fn fix_bytecode_version(
+pub(crate) fn fix_bytecode_version(
     bytecode_version_in: Option<u32>,
     language_version: Option<LanguageVersion>,
 ) -> Option<u32> {
@@ -814,7 +814,7 @@ impl FromStr for IncludedArtifacts {
     }
 }
 
-fn experiments_from_opt_level(optlevel: &Option<OptimizationLevel>) -> Vec<String> {
+pub(crate) fn experiments_from_opt_level(optlevel: &Option<OptimizationLevel>) -> Vec<String> {
     match optlevel {
         None | Some(OptimizationLevel::Default) => {
             vec![format!("{}=on", Experiment::OPTIMIZE.to_string())]
```

### third_party/move/tools/move-cli/src/base/coverage.rs
```diff
@@ -5,8 +5,10 @@ use super::reroot_path;
 use clap::*;
 use move_compiler::compiled_unit::{CompiledUnit, NamedCompiledModule};
 use move_coverage::{
-    coverage_map::CoverageMap, format_csv_summary, format_human_summary,
-    source_coverage::SourceCoverageBuilder, summary::summarize_inst_cov,
+    coverage_map::CoverageMap,
+    format_csv_summary, format_human_summary,
+    source_coverage::{ColorChoice, SourceCoverageBuilder, TextIndicator},
+    summary::summarize_inst_cov,
 };
 use move_disassembler::disassembler::Disassembler;
 use move_package::BuildConfig;
@@ -45,6 +47,14 @@ pub enum CoverageSummaryOptions {
 pub struct Coverage {
     #[clap(subcommand)]
     pub options: CoverageSummaryOptions,
+
+    /// Colorize output based on coverage
+    #[clap(long, default_value_t = ColorChoice::Default)]
+    pub color: ColorChoice,
+
+    /// Tag each line with a textual indication of coverage
+    #[clap(long, default_value_t = TextIndicator::Explicit)]
+    pub tag: TextIndicator,
 }
 
 impl Coverage {
@@ -69,10 +79,11 @@ impl Coverage {
                     }) => (module, source_map),
                     _ => panic!("Should all be modules"),
                 };
-                let source_coverage = SourceCoverageBuilder::new(module, &coverage_map, source_map);
+                let source_coverage_builder =
+                    SourceCoverageBuilder::new(module, &coverage_map, source_map);
+                let source_coverage = source_coverage_builder.compute_source_coverage(source_path);
                 source_coverage
-                    .compute_source_coverage(source_path)
-                    .output_source_coverage(&mut std::io::stdout())
+                    .output_source_coverage(&mut std::io::stdout(), self.color, self.tag)
                     .unwrap();
             },
             CoverageSummaryOptions::Summary {
```

### third_party/move/tools/move-coverage/src/bin/source-coverage.rs
```diff
@@ -8,7 +8,10 @@ use clap::Parser;
 use move_binary_format::file_format::CompiledModule;
 use move_bytecode_source_map::utils::source_map_from_file;
 use move_command_line_common::files::SOURCE_MAP_EXTENSION;
-use move_coverage::{coverage_map::CoverageMap, source_coverage::SourceCoverageBuilder};
+use move_coverage::{
+    coverage_map::CoverageMap,
+    source_coverage::{ColorChoice, SourceCoverageBuilder, TextIndicator},
+};
 use std::{
     fs,
     fs::File,
@@ -39,6 +42,12 @@ struct Args {
     /// Optional path to save coverage. Printed to stdout if not present.
     #[clap(long = "coverage-path", short = 'o')]
     pub coverage_path: Option<String>,
+    /// Colorize output based on coverage
+    #[clap(long, default_value_t = ColorChoice::Default)]
+    pub color: ColorChoice,
+    /// Tag each line with a textual indication of coverage
+    #[clap(long, default_value_t = TextIndicator::Explicit)]
+    pub tag: TextIndicator,
 }
 
 fn main() {
@@ -69,9 +78,9 @@ fn main() {
         None => Box::new(io::stdout()),
     };
 
-    source_cov
-        .compute_source_coverage(source_path)
-        .output_source_coverage(&mut coverage_writer)
+    let source_coverage = source_cov.compute_source_coverage(source_path);
+    source_coverage
+        .output_source_coverage(&mut coverage_writer, args.color, args.tag)
         .unwrap();
 }
 
```

### third_party/move/tools/move-coverage/src/source_coverage.rs
```diff
@@ -5,22 +5,26 @@
 #![forbid(unsafe_code)]
 
 use crate::coverage_map::CoverageMap;
+use clap::ValueEnum;
 use codespan::{Files, Span};
-use colored::*;
+use colored::{self, Colorize};
 use move_binary_format::{
     access::ModuleAccess,
     file_format::{CodeOffset, FunctionDefinitionIndex},
     CompiledModule,
 };
 use move_bytecode_source_map::source_map::SourceMap;
+use move_command_line_common::files::FileHash;
 use move_core_types::identifier::Identifier;
 use move_ir_types::location::Loc;
 use serde::Serialize;
 use std::{
     collections::BTreeMap,
+    fmt::{Display, Formatter},
     fs,
     io::{self, Write},
     path::Path,
+    str::FromStr,
 };
 
 #[derive(Clone, Debug, Serialize)]
@@ -42,6 +46,116 @@ pub enum AbstractSegment {
     BoundedLeft { start: u32 },
 }
 
+/// Option to control use of color escape codes in coverage output
+/// to indicate source code coverage.  Unless `None`
+/// is selected, code which is covered is green, uncovered
+/// code is red.  By `Default`, color is only shown when
+/// output goes to a terminal.  If `Always`, then color
+/// escapes are included in the output even to a file
+/// or other program.
+#[derive(ValueEnum, Clone, Debug, Serialize)]
+pub enum ColorChoice {
+    /// Color is never shown
+    None,
+    /// Color is shown only on a terminal
+    Default,
+    /// Color is always shown
+    Always,
+}
+
+impl Display for ColorChoice {
+    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
+        use ColorChoice::*;
+        match self {
+            None => f.write_str("none"),
+            Default => f.write_str("default"),
+            Always => f.write_str("always"),
+        }
+    }
+}
+
+impl FromStr for ColorChoice {
+    type Err = &'static str;
+
+    fn from_str(s: &str) -> Result<Self, Self::Err> {
+        use ColorChoice::*;
+        match s {
+            "none" => Ok(None),
+            "default" => Ok(Default),
+            "always" => Ok(Always),
+            _ => Err("unknown variant"),
+        }
+    }
+}
+
+/// Option to control use of explicit textual indication of lines
+/// covered or not in test coverage listings.  If `On` or
+/// `Explicit` is selected, then lines with missing coverage
+/// are tagged with `-`; otherwise, they have `+`.
+#[derive(ValueEnum, Clone, Debug, Serialize)]
+pub enum TextIndicator {
+    /// No textual indicator of coverage.
+    None,
+    /// Prefix each line with some code missing coverage by `-`;
+    /// other lines are prefixed with `+`.
+    Explicit,
+    /// Same behavior as Explicit.
+    On,
+}
+
+impl Display for TextIndicator {
+    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
+        use TextIndicator::*;
+        match self {
+            None => f.write_str("none"),
+            Explicit => f.write_str("explicit"),
+            On => f.write_str("on"),
+        }
+    }
+}
+
+impl FromStr for TextIndicator {
+    type Err = &'static str;
+
+    fn from_str(s: &str) -> Result<Self, Self::Err> {
+        use TextIndicator::*;
+        match s {
+            "none" => Ok(None),
+            "explicit" => Ok(Explicit),
+            "on" => Ok(On),
+            _ => Err("unknown variant"),
+        }
+    }
+}
+
+impl ColorChoice {
+    fn execute(&self) {
+        use ColorChoice::*;
+        match self {
+            None => {
+                colored::control::set_override(false);
+            },
+            Default => {},
+            Always => {
+                colored::control::set_override(true);
+            },
+        }
+    }
+
+    fn undo(&self) {
+        use ColorChoice::*;
+        match self {
+            None => {
+                colored::control::unset_override();
+            },
+            Default => {},
+            Always => {
+                colored::control::unset_override();
+            },
+        }
+    }
+}
+
 #[derive(Debug, Serialize)]
 pub enum StringSegment {
     Covered(String),
@@ -136,15 +250,17 @@ impl<'a> SourceCoverageBuilder<'a> {
         let file_contents = fs::read_to_string(file_path).unwrap();
         assert!(
             self.source_map.check(&file_contents),
-            "File contents out of sync with source map"
+            "File contents {} out of sync with source map",
+            file_path.display()
         );
+        let file_hash = self.source_map.definition_location.file_hash();
         let mut files = Files::new();
         let file_id = files.add(file_path.as_os_str().to_os_string(), file_contents.clone());
 
         let mut uncovered_segments = BTreeMap::new();
 
-        for (_, fn_cov) in self.uncovered_locations.iter() {
-            for span in merge_spans(fn_cov.clone()).into_iter() {
+        for (_key, fn_cov) in self.uncovered_locations.iter() {
+            for span in merge_spans(file_hash, fn_cov.clone()).into_iter() {
                 let start_loc = files.location(file_id, span.start()).unwrap();
                 let end_loc = files.location(file_id, span.end()).unwrap();
                 let start_line = start_loc.line.0;
@@ -177,6 +293,7 @@ impl<'a> SourceCoverageBuilder<'a> {
                 }
             }
         }
+        uncovered_segments.values_mut().for_each(|v| v.sort());
 
         let mut annotated_lines = Vec::new();
         for (line_number, mut line) in file_contents.lines().map(|x| x.to_owned()).enumerate() {
@@ -226,8 +343,40 @@ impl<'a> SourceCoverageBuilder<'a> {
 }
 
 impl SourceCoverage {
-    pub fn output_source_coverage<W: Write>(&self, output_writer: &mut W) -> io::Result<()> {
+    pub fn output_source_coverage<W: Write>(
+        &self,
+        output_writer: &mut W,
+        color: ColorChoice,
+        text_indicator: TextIndicator,
+    ) -> io::Result<()> {
+        color.execute();
+        let be_explicit = match text_indicator {
+            TextIndicator::Explicit | TextIndicator::On => {
+                write!(
+                    output_writer,
+                    "Code coverage per line of code:\n  {} indicates the line is not executable or is fully covered during execution\n  {} indicates the line is executable but NOT fully covered during execution\nSource code follows:\n",
+                    "+".to_string().green(),
+                    "-".to_string().bold().red(),
+                )?;
+                true
+            },
+            TextIndicator::None => false,
+        };
         for line in self.annotated_lines.iter() {
+            if be_explicit {
+                let has_uncovered = line
+                    .iter()
+                    .any(|string_segment| matches!(string_segment, StringSegment::Uncovered(_)));
+                write!(
+                    output_writer,
+                    "{} ",
+                    if has_uncovered {
+                        "-".to_string().red()
+                    } else {
+                        "+".to_string().green()
+                    }
+                )?;
+            }
             for string_segment in line.iter() {
                 match string_segment {
                     StringSegment::Covered(s) => write!(output_writer, "{}", s.green())?,
@@ -236,20 +385,25 @@ impl SourceCoverage {
             }
             writeln!(output_writer)?;
         }
+        color.undo();
         Ok(())
     }
 }
 
-fn merge_spans(cov: FunctionSourceCoverage) -> Vec<Span> {
+fn merge_spans(file_hash: FileHash, cov: FunctionSourceCoverage) -> Vec<Span> {
     if cov.uncovered_locations.is_empty() {
         return vec![];
     }
 
     let mut covs: Vec<_> = cov
         .uncovered_locations
         .iter()
+        .filter(|loc| loc.file_hash() == file_hash)
         .map(|loc| Span::new(loc.start(), loc.end()))
         .collect();
+    if covs.is_empty() {
+        return vec![];
+    }
     covs.sort();
 
     let mut unioned = Vec::new();
```

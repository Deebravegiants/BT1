# [?] fix(debugger): crash when stepping through locations spanning multiple lines (#3920)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-01-02
Source: https://github.com/noir-lang/noir/commit/223e860975c2698bd5043340b937de74552ec15b
Type: security-commit

## Details
fix(debugger): crash when stepping through locations spanning multiple lines (#3920)

# Description

The debugger REPL was failing under certain scenarios when a stepped
location spanned multiple lines. We tracked down the failure to a
missing bounds check.

This PR fixes the issue, introduces a refactor to make the relevant code
testable, and adds regression tests to prevent reoccurrence.

This PR is best reviewed as a whole instead of commit-by-commit.

## Summary

- Moves source code printing logic from the main debugger REPL module,
to a new source_code_printer module.
- Decouples actual printing from rendering logic to improve testability.
- Adds regression tests

## Documentation

Check one:
- [ ] No documentation needed.
- [x] Documentation included in this PR.
- [ ] **[Exceptional Case]** Documentation to be submitted in a separate
PR.

# PR Checklist\*

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### Cargo.lock
```diff
@@ -2779,6 +2779,7 @@ dependencies = [
  "noirc_printable_type",
  "owo-colors",
  "serde_json",
+ "tempfile",
  "thiserror",
 ]
 
```

### tooling/debugger/Cargo.toml
```diff
@@ -20,4 +20,7 @@ codespan-reporting.workspace = true
 dap.workspace = true
 easy-repl = "0.2.1"
 owo-colors = "3"
-serde_json.workspace = true
\ No newline at end of file
+serde_json.workspace = true
+
+[dev_dependencies]
+tempfile.workspace = true
\ No newline at end of file
```

### tooling/debugger/src/lib.rs
```diff
@@ -1,6 +1,7 @@
 mod context;
 mod dap;
 mod repl;
+mod source_code_printer;
 
 use std::io::{Read, Write};
 
```

### tooling/debugger/src/repl.rs
```diff
@@ -9,12 +9,7 @@ use nargo::{artifacts::debug::DebugArtifact, ops::DefaultForeignCallExecutor, Na
 use easy_repl::{command, CommandStatus, Repl};
 use std::cell::RefCell;
 
-use codespan_reporting::files::Files;
-use noirc_errors::Location;
-
-use owo_colors::OwoColorize;
-
-use std::ops::Range;
+use crate::source_code_printer::print_source_code_location;
 
 pub struct ReplDebugger<'a, B: BlackBoxFunctionSolver> {
     context: DebugContext<'a, B>,
@@ -70,73 +65,7 @@ impl<'a, B: BlackBoxFunctionSolver> ReplDebugger<'a, B> {
                         );
                     }
                 }
-                self.show_source_code_location(&location);
-            }
-        }
-    }
-
-    fn print_location_path(&self, loc: Location) {
-        let line_number = self.debug_artifact.location_line_number(loc).unwrap();
-        let column_number = self.debug_artifact.location_column_number(loc).unwrap();
-
-        println!(
-            "At {}:{line_number}:{column_number}",
-            self.debug_artifact.name(loc.file).unwrap()
-        );
-    }
-
-    fn show_source_code_location(&self, location: &OpcodeLocation) {
-        let locations = self.debug_artifact.debug_symbols[0].opcode_location(location);
-        let Some(locations) = locations else { return };
-        for loc in locations {
-            self.print_location_path(loc);
-
-            let loc_line_index = self.debug_artifact.location_line_index(loc).unwrap();
-
-            // How many lines before or after the location's line we
-            // print
-            let context_lines = 5;
-
-            let first_line_to_print =
-                if loc_line_index < context_lines { 0 } else { loc_line_index - context_lines };
-
-            let last_line_index = self.debug_artifact.last_line_index(loc).unwrap();
-            let last_line_to_print = std::cmp::min(loc_line_index + context_lines, last_line_index);
-
-            let source = self.debug_artifact.location_source_code(loc).unwrap();
-            for (current_line_index, line) in source.lines().enumerate() {
-                let current_line_number = current_line_index + 1;
-
-                if current_line_index < first_line_to_print {
-                    // Ignore lines before range starts
-                    continue;
-                } else if current_line_index == first_line_to_print && current_line_index > 0 {
-                    // Denote that there's more lines before but we're not showing them
-                    print_line_of_ellipsis(current_line_index);
-                }
-
-                if current_line_index > last_line_to_print {
-                    // Denote that there's more lines after but we're not showing them,
-                    // and stop printing
-                    print_line_of_ellipsis(current_line_number);
-                    break;
-                }
-
-                if current_line_index == loc_line_index {
-                    // Highlight current location
-                    let Range { start: loc_start, end: loc_end } =
-                        self.debug_artifact.location_in_line(loc).unwrap();
-                    println!(
-                        "{:>3} {:2} {}{}{}",
-                        current_line_number,
-                        "->",
-                        &line[0..loc_start].to_string().dimmed(),
-                        &line[loc_start..loc_end],
-                        &line[loc_end..].to_string().dimmed()
-                    );
-                } else {
-                    print_dimmed_line(current_line_number, line);
-                }
+                print_source_code_location(self.debug_artifact, &location);
             }
         }
     }
@@ -384,14 +313,6 @@ impl<'a, B: BlackBoxFunctionSolver> ReplDebugger<'a, B> {
     }
 }
 
-fn print_line_of_ellipsis(line_number: usize) {
-    println!("{}", format!("{:>3} {}", line_number, "...").dimmed());
-}
-
-fn print_dimmed_line(line_number: usize, line: &str) {
-    println!("{}", format!("{:>3} {:2} {}", line_number, "", line).dimmed());
-}
-
 pub fn run<B: BlackBoxFunctionSolver>(
     blackbox_solver: &B,
     circuit: &Circuit,
```

### tooling/debugger/src/source_code_printer.rs
```diff
@@ -0,0 +1,317 @@
+use acvm::acir::circuit::OpcodeLocation;
+use codespan_reporting::files::Files;
+use nargo::artifacts::debug::DebugArtifact;
+use noirc_errors::Location;
+use owo_colors::OwoColorize;
+use std::ops::Range;
+
+#[derive(Debug, PartialEq)]
+enum PrintedLine<'a> {
+    Skip,
+    Ellipsis {
+        line_number: usize,
+    },
+    Content {
+        line_number: usize,
+        cursor: &'a str,
+        content: &'a str,
+        highlight: Option<Range<usize>>,
+    },
+}
+
+#[derive(Clone, Debug)]
+struct LocationPrintContext {
+    file_lines: Range<usize>,
+    printed_lines: Range<usize>,
+    location_lines: Range<usize>,
+    location_offset_in_first_line: Range<usize>,
+    location_offset_in_last_line: Range<usize>,
+}
+
+// Given a DebugArtifact and an OpcodeLocation, prints all the source code
+// locations the OpcodeLocation maps to, with some surrounding context and
+// visual aids to highlight the location itself.
+pub(crate) fn print_source_code_location(
+    debug_artifact: &DebugArtifact,
+    location: &OpcodeLocation,
+) {
+    let locations = debug_artifact.debug_symbols[0].opcode_location(location);
+    let Some(locations) = locations else { return; };
+
+    let locations = locations.iter();
+
+    for loc in locations {
+        print_location_path(debug_artifact, *loc);
+
+        let lines = render_location(debug_artifact, loc);
+
+        for line in lines {
+            match line {
+                PrintedLine::Skip => {}
+                PrintedLine::Ellipsis { line_number } => print_ellipsis(line_number),
+                PrintedLine::Content { line_number, cursor, content, highlight } => {
+                    print_content(line_number, cursor, content, highlight)
+                }
+            }
+        }
+    }
+}
+
+fn print_location_path(debug_artifact: &DebugArtifact, loc: Location) {
+    let line_number = debug_artifact.location_line_number(loc).unwrap();
+    let column_number = debug_artifact.location_column_number(loc).unwrap();
+
+    println!("At {}:{line_number}:{column_number}", debug_artifact.name(loc.file).unwrap());
+}
+
+fn print_ellipsis(line_number: usize) {
+    println!("{:>3} {:2} {}", line_number.dimmed(), "", "...".dimmed());
+}
+
+fn print_content(line_number: usize, cursor: &str, content: &str, highlight: Option<Range<usize>>) {
+    match highlight {
+        Some(highlight) => {
+            println!(
+                "{:>3} {:2} {}{}{}",
+                line_number,
+                cursor,
+                content[0..highlight.start].to_string().dimmed(),
+                &content[highlight.start..highlight.end],
+                content[highlight.end..].to_string().dimmed(),
+            );
+        }
+        None => {
+            println!(
+                "{:>3} {:2} {}",
+                line_number.dimmed(),
+                cursor.dimmed(),
+                content.to_string().dimmed(),
+            );
+        }
+    }
+}
+
+fn render_line(
+    current: usize,
+    content: &str,
+    loc_context: LocationPrintContext,
+) -> PrintedLine<'_> {
+    let file_lines = loc_context.file_lines;
+    let printed_lines = loc_context.printed_lines;
+    let location_lines = loc_context.location_lines;
+    let line_number = current + 1;
+
+    if current < printed_lines.start {
+        // Ignore lines before the context window we choose to show
+        PrintedLine::Skip
+    } else if 0 < current && current == printed_lines.start && current < location_lines.start {
+        // Denote that there's more lines before but we're not showing them
+        PrintedLine::Ellipsis { line_number }
+    } else if current < location_lines.start {
+        // Print lines before the location start without highlighting
+        PrintedLine::Content { line_number, cursor: "", content, highlight: None }
+    } else if current == location_lines.start {
+        // Highlight current location from where it starts to the end of the current line
+        PrintedLine::Content {
+            line_number,
+            cursor: "->",
+            content,
+            highlight: Some(loc_context.location_offset_in_first_line),
+        }
+    } else if current < location_lines.end {
+        // Highlight current line if it's contained by the current location
+        PrintedLine::Content {
+            line_number,
+            cursor: "",
+            content,
+            highlight: Some(Range { start: 0, end: content.len() }),
+        }
+    } else if current == location_lines.end {
+        // Highlight current location from the beginning of the line until the location's own end
+        PrintedLine::Content {
+            line_number,
+            cursor: "",
+            content,
+            highlight: Some(loc_context.location_offset_in_last_line),
+        }
+    } else if current < printed_lines.end || printed_lines.end == file_lines.end {
+        // Print lines after the location end without highlighting
+        PrintedLine::Content { line_number, cursor: "", content, highlight: None }
+    } else if current == printed_lines.end && printed_lines.end < file_lines.end {
+        // Denote that there's more lines after but we're not showing them
+        PrintedLine::Ellipsis { line_number }
+    } else {
+        PrintedLine::Skip
+    }
+}
+
+// Given a Location in a DebugArtifact, returns a line iterator that specifies how to
+// print the location's file.
+//
+// Consider for example the file (line numbers added to facilitate this doc):
+// ```
+// 1 use dep::std::hash::poseidon;
+// 2
+// 3 fn main(x1: [Field; 2], y1: pub Field, x2: [Field; 4], y2: pub Field) {
+// 4    let hash1 = poseidon::bn254::hash_2(x1);
+// 5    assert(hash1 == y1);
+// 6
+// 7    let hash2 = poseidon::bn254::hash_4(x2);
+// 8    assert(hash2 == y2);
+// 9 }
+// 10
+// ```
+//
+// If the location to render is `poseidon::bn254::hash_2(x1)`, we'll render the file as:
+// ```
+// 1   use dep::std::hash::poseidon;
+// 2
+// 3   fn main(x1: [Field; 2], y1: pub Field, x2: [Field; 4], y2: pub Field) {
+// 4      let hash1 = <b>poseidon::bn254::hash_2(x1)</b>;
+// 5 ->   assert(hash1 == y1);
+// 6
+// 7      let hash2 = poseidon::bn254::hash_4(x2);
+// 8      assert(hash2 == y2);
+// 9   }
+// 10  ...
+// ```
+//
+// This is the result of:
+// 1. Limiting the amount of printed lines to 5 before and 5 after the location.
+// 2. Using ellipsis (...) to denote when some file lines have been left out of the render.
+// 3. Using an arrow cursor (->) to denote where the rendered location starts.
+// 4. Highlighting the location (here expressed as a <b/> block for the sake of the explanation).
+//
+// Note that locations may span multiple lines, so this function deals with that too.
+fn render_location<'a>(
+    debug_artifact: &'a DebugArtifact,
+    loc: &'a Location,
+) -> impl Iterator<Item = PrintedLine<'a>> {
+    let loc = *loc;
+
+    let file_lines = Range { start: 0, end: debug_artifact.last_line_index(loc).unwrap() };
+
+    // Sub-range of file lines that this location spans
+    let location_lines = Range {
+        start: debug_artifact.location_line_index(loc).unwrap(),
+        end: debug_artifact.location_end_line_index(loc).unwrap(),
+    };
+
+    // How many lines before or after the location's lines we print
+    let context_lines = 5;
+
+    // Sub-range of lines that we'll print, which includes location + context lines
+    let first_line_to_print =
+        if location_lines.start < context_lines { 0 } else { location_lines.start - context_lines };
+    let last_line_to_print = std::cmp::min(location_lines.end + context_lines, file_lines.end);
+    let printed_lines = Range { start: first_line_to_print, end: last_line_to_print };
+
+    // Range of the location relative to its starting and ending lines
+    let location_offset_in_first_line = debug_artifact.location_in_line(loc).unwrap();
+    let location_offset_in_last_line = debug_artifact.location_in_end_line(loc).unwrap();
+
+    let context = LocationPrintContext {
+        file_lines,
+        printed_lines,
+        location_lines,
+        location_offset_in_first_line,
+        location_offset_in_last_line,
+    };
+
+    let source = debug_artifact.location_source_code(loc).unwrap();
+    source
+        .lines()
+        .enumerate()
+        .map(move |(index, content)| render_line(index, content, context.clone()))
+}
+
+#[cfg(test)]
+mod tests {
+    use crate::source_code_printer::render_location;
+    use crate::source_code_printer::PrintedLine::Content;
+    use acvm::acir::circuit::OpcodeLocation;
+    use fm::FileManager;
+    use nargo::artifacts::debug::DebugArtifact;
+    use noirc_errors::{debug_info::DebugInfo, Location, Span};
+    use std::collections::BTreeMap;
+    use std::ops::Range;
+    use std::path::Path;
+    use std::path::PathBuf;
+    use tempfile::{tempdir, TempDir};
+
+    // Returns the absolute path to the file
+    fn create_dummy_file(dir: &TempDir, file_name: &Path) -> PathBuf {
+        let file_path = dir.path().join(file_name);
+        let _file = std::fs::File::create(&file_path).unwrap();
+        file_path
+    }
+
+    #[test]
+    fn render_multiple_line_location() {
+        let source_code = r##"pub fn main(mut state: [Field; 2]) -> [Field; 2] {
+    state = permute(
+        consts::x5_2_config(),
+        state);
+
+    state
+}"##;
+
+        let dir = tempdir().unwrap();
+        let file_name = Path::new("main.nr");
+        create_dummy_file(&dir, file_name);
+
+        let mut fm = FileManager::new(dir.path());
+        let file_id = fm.add_file_with_source(file_name, source_code.to_string()).unwrap();
+
+        // Location of
+        // ```
+        // permute(
+        //      consts::x5_2_config(),
+        //      state)
+        // ```
+        let loc = Location::new(Span::inclusive(63, 116), file_id);
+
+        // We don't care about opcodes in this context,
+        // we just use a dummy to construct debug_symbols
+        let mut opcode_locations = BTreeMap::<OpcodeLocation, Vec<Location>>::new();
+        opcode_locations.insert(OpcodeLocation::Acir(42), vec![loc]);
+
+        let debug_symbols = vec![DebugInfo::new(opcode_locations)];
+        let debug_artifact = DebugArtifact::new(debug_symbols, &fm);
+
+        let location_rendered: Vec<_> = render_location(&debug_artifact, &loc).collect();
+
+        assert_eq!(
+            location_rendered,
+            vec![
+                Content {
+                    line_number: 1,
+                    cursor: "",
+                    content: "pub fn main(mut state: [Field; 2]) -> [Field; 2] {",
+                    highlight: None,
+                },
+                Content {
+                    line_number: 2,
+                    cursor: "->",
+                    content: "    state = permute(",
+                    highlight: Some(Range { start: 12, end: 20 }),
+                },
+                Content {
+                    line_number: 3,
+                    cursor: "",
+                    content: "        consts::x5_2_config(),",
+                    highlight: Some(Range { start: 0, end: 30 }),
+                },
+                Content {
+                    line_number: 4,
+                    cursor: "",
+                    content: "        state);",
+                    highlight: Some(Range { start: 0, end: 14 }),
+                },
+                Content { line_number: 5, cursor: "", content: "", highlight: None },
+                Content { line_number: 6, cursor: "", content: "    state", highlight: None },
+                Content { line_number: 7, cursor: "", content: "}", highlight: None },
+            ]
+        );
+    }
+}
```

### tooling/nargo/src/artifacts/debug.rs
```diff
@@ -59,6 +59,12 @@ impl DebugArtifact {
         self.line_index(location.file, location_start)
     }
 
+    /// Given a location, returns the index of the line it ends at
+    pub fn location_end_line_index(&self, location: Location) -> Result<usize, Error> {
+        let location_end = location.span.end() as usize;
+        self.line_index(location.file, location_end)
+    }
+
     /// Given a location, returns the line number it starts at
     pub fn location_line_number(&self, location: Location) -> Result<usize, Error> {
         let location_start = location.span.start() as usize;
@@ -82,12 +88,28 @@ impl DebugArtifact {
         let line_index = self.line_index(location.file, location_start)?;
         let line_span = self.line_range(location.file, line_index)?;
 
+        let line_length = line_span.end - (line_span.start + 1);
         let start_in_line = location_start - line_span.start;
+
+        // The location might continue beyond the line,
+        // so we need a bounds check
         let end_in_line = location_end - line_span.start;
+        let end_in_line = std::cmp::min(end_in_line, line_length);
 
         Ok(Range { start: start_in_line, end: end_in_line })
     }
 
+    /// Given a location, returns a Span relative to its last line's
+    /// position in the file. This is useful when processing a file's
+    /// contents on a per-line-basis.
+    pub fn location_in_end_line(&self, location: Location) -> Result<Range<usize>, Error> {
+        let end_line_index = self.location_end_line_index(location)?;
+        let line_span = self.line_range(location.file, end_line_index)?;
+        let location_end = location.span.end() as usize;
+        let end_in_line = location_end - line_span.start;
+        Ok(Range { start: 0, end: end_in_line })
+    }
+
     /// Given a location, returns the last line index
     /// of its file
     pub fn last_line_index(&self, location: Location) -> Result<usize, Error> {
@@ -149,3 +171,70 @@ impl<'a> Files<'a> for DebugArtifact {
         })
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use crate::artifacts::debug::DebugArtifact;
+    use acvm::acir::circuit::OpcodeLocation;
+    use fm::FileManager;
+    use noirc_errors::{debug_info::DebugInfo, Location, Span};
+    use std::collections::BTreeMap;
+    use std::ops::Range;
+    use std::path::Path;
+    use std::path::PathBuf;
+    use tempfile::{tempdir, TempDir};
+
+    // Returns the absolute path to the file
+    fn create_dummy_file(dir: &TempDir, file_name: &Path) -> PathBuf {
+        let file_path = dir.path().join(file_name);
+        let _file = std::fs::File::create(&file_path).unwrap();
+        file_path
+    }
+
+    // Tests that location_in_line correctly handles
+    // locations spanning multiple lines.
+    // For example, given the snippet:
+    // ```
+    // permute(
+    //    consts::x5_2_config(),
+    //    state);
+    // ```
+    // We want location_in_line to return the range
+    // containing `permute(`
+    #[test]
+    fn location_in_line_stops_at_end_of_line() {
+        let source_code = r##"pub fn main(mut state: [Field; 2]) -> [Field; 2] {
+    state = permute(
+        consts::x5_2_config(),
+        state);
+
+    state
+}"##;
+
+        let dir = tempdir().unwrap();
+        let file_name = Path::new("main.nr");
+        create_dummy_file(&dir, file_name);
+
+        let mut fm = FileManager::new(dir.path());
+        let file_id = fm.add_file_with_source(file_name, source_code.to_string()).unwrap();
+
+        // Location of
+        // ```
+        // permute(
+        //      consts::x5_2_config(),
+        //      state)
+        // ```
+        let loc = Location::new(Span::inclusive(63, 116), file_id);
+
+        // We don't care about opcodes in this context,
+        // we just use a dummy to construct debug_symbols
+        let mut opcode_locations = BTreeMap::<OpcodeLocation, Vec<Location>>::new();
+        opcode_locations.insert(OpcodeLocation::Acir(42), vec![loc]);
+
+        let debug_symbols = vec![DebugInfo::new(opcode_locations)];
+        let debug_artifact = DebugArtifact::new(debug_symbols, &fm);
+
+        let location_in_line = debug_artifact.location_in_line(loc).expect("Expected a range");
+        assert_eq!(location_in_line, Range { start: 12, end: 20 });
+    }
+}
```

# [?] fix a crash when file has non-English letters (#3638)

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2026-08-24
Source: https://github.com/0xMiden/miden-vm/commit/ceb221be8f600d02bfd9b7c907a6067326377e21
Type: security-commit

## Details
fix a crash when file has non-English letters (#3638)

* fix(debug-types): line_column_to_offset counts columns in characters, not bytes

line_column_to_offset() converts a (line, column) position into a byte
offset within the file. It treated `column_index` as a raw byte offset
into the line's UTF-8 string and split the string at that byte position
directly. `column`, however, is meant to count *characters*, matching
`location()` (the inverse function), which computes columns via
`chars().count()`.

For any line containing a multi-byte UTF-8 character, this was wrong two
ways:
- If the target byte offset happened to fall on a char boundary but past
  a multi-byte character, the returned offset was short by the extra
  bytes that character took up (silently wrong result).
- If the target byte offset landed inside a multi-byte character's
  encoding (not on a char boundary at all), `str::split_at` panics.

Example: "héllo" -- 'é' is 2 bytes in UTF-8. Asking for column 1 (the
position right after 'h') used byte offset 1, which lands between 'é's
two bytes and is not a valid split point, and would panic. Column 2 (the
position right after 'é') used byte offset 2, but the correct byte offset
is 3, since 'é' occupies bytes 1-2.

Fix: find the byte offset of the `column_index`-th character via
`char_indices()` instead of using `column_index` directly as a byte
offset. The one-past-the-end case (column_index == the line's character
count) still resolves to the line's byte length, matching prior
behavior for the end-of-line position; anything further returns None
as before.

Adds a regression test covering every character position on a line with
a multi-byte character, including the position immediately following it
(the case that used to be wrong), and round-trips each result back
through `location()` to confirm both functions agree on what "column N"
means.

Fixes #3633.

Note: this environment has no Rust toolchain new enough to compile this
crate (same constraint as prior contributions to this repo), so this
could not be run locally. I traced the UTF-8 byte layout of the test
string by hand (verified independently in Python, since UTF-8 encoding
is a fixed specification, not something that needs `rustc` to check) and
walked both the fix and the test through the exact byte/char offsets
they'd produce. Please run `cargo test -p miden-debug-types` before
merging.

* fix(debug-types): address review feedback on line_column_to_offset

Addresses three points from huitseeker's review of the multibyte-UTF-8
fix:

1. Avoid scanning the line twice. The fallback path called
   line_src.chars().count() to detect "column is exactly at the end of
   the line" after nth() had already exhausted char_indices() to look
   for it. Chain the content's byte length onto the char boundaries and
   call nth() once, covering both cases in a single pass.

2. Reject columns that land on or inside a line's terminator ("\n" or
   "\r\n"). That byte range is only reachable by moving to the start of
   the next line. Without this, update() could be handed a same-line
   selection (start.line == end.line) whose byte range actually spanned
   the terminator -- e.g. columns 1..2 of line 0 in "a\nb" target the
   "\n" itself -- corrupting the incrementally-maintained line_starts
   bookkeeping instead of being rejected. Added a regression test
   reproducing exactly that scenario through update(), plus a direct
   test for both "\n" and "\r\n" terminators.

3. Document and pin the Unicode-scalar-vs-UTF-16 column contract.
   char_indices() counts Unicode scalar values, matching location()
   (which reports columns via chars().count()), not UTF-16 code units
   as used by the Language Server Protocol. masm-lsp isn't in this
   repo, so it can't be fixed here; documented the contract on
   line_column_to_offset and added a test with an astral character
   (outside the Basic Multilingual Plane) that pins the scalar-based
   behavior and spells out where it disagrees with an unconverted LSP
   column, so a caller bridging from LSP knows to convert first.

Note: still no Rust toolchain available in this environment to compile
this crate, so please run the crate's test suite before merging.

* docs(debug-types): trim narration per review, state the contract plainly

Addresses two more nits from huitseeker's review:

1. line_column_to_offset's doc comment now just states the contract
   (chars, not bytes or UTF-16; terminators are out of bounds) instead
   of walking through the failure modes that motivated it.

2. Dropped the test doc comments and most inline narration on the four
   line_column_to_offset/update tests; the test code and assertions
   already show each case, kept only the UTF-8/UTF-16 byte-width facts
   that aren't otherwise obvious from the code.

No functional change.

* refactor(debug-types): simplify terminator stripping in line_column_to_offset

Addresses another nit from huitseeker's review: use
strip_suffix("\r\n").or_else(|| strip_suffix('\n')).unwrap_or(line_src)
to get the terminator-free content directly, instead of manually
computing terminator_len and slicing by it. Same behavior, states the
operation directly instead of via index arithmetic.

No functional change.

* docs: add changelog entry for the line_column_to_offset fix

This PR never touched CHANGELOG.md, which this repo's changelog check
requires for every PR. Added an entry under "Changes" for #3633,
matching the style of nearby entries.

* docs(debug-types): shorten line_column_to_offset comments per review

Addresses four more nits from huitseeker's review:

1. Shortened the function's doc comment to state the contract plainly:
   columns count Unicode scalars, the content-end position is valid,
   positions inside a trailing terminator are not, and LSP callers must
   convert UTF-16 columns first. Drops the earlier wording's confusing
   claim about the terminator's position being reachable via the next
   line's column 0, since that's a different byte offset.
2. Same wording, requested again on a second pass.
3. Dropped the comment above the strip_suffix chain; the chain itself
   already says what it does.
4. Shortened the comment above the char_indices/chain to state what it
   does rather than why, since the code already shows the how.

No functional change.

---------

Co-authored-by: François Garillot <4142+huitseeker@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -13,6 +13,7 @@
 
 #### Changes
 
+- Fixed `line_column_to_offset` treating the column index as a raw byte offset instead of a character offset, which returned the wrong offset or panicked for lines containing multi-byte UTF-8 characters ([#3633](https://github.com/0xMiden/miden-vm/issues/3633)).
 - Clarified the ACE circuit trust model and distinguished the order-independent AIR wiring relation from the standard processor's sequential DAG witness construction ([#3683](https://github.com/0xMiden/miden-vm/pull/3683)).
 - [BREAKING] Removed the MASM `sys::vm::claim::kernel_commitment` procedure. The recursive verifier now copies and hashes kernel digests from advice in one pass using the new `mem::pipe_words_to_memory_in_domain` procedure. Callers computing a domain-tagged hash over an existing memory region can use `crypto::hashes::poseidon2::hash_elements_in_domain` directly.
 - Documented the `word("...")` and `event("...")` string-derived constant constructors and word
```

### crates/debug-types/src/source_file.rs
```diff
@@ -640,6 +640,9 @@ impl SourceContent {
 
     /// Get the [ByteIndex] corresponding to the given line and column indices.
     ///
+    /// Columns count Unicode scalars. The content-end position is valid; positions inside a
+    /// trailing terminator are not. LSP callers must convert UTF-16 columns first.
+    ///
     /// Returns `None` if the line or column indices are out of bounds.
     pub fn line_column_to_offset(
         &self,
@@ -652,12 +655,20 @@ impl SourceContent {
             .content
             .get(line_span.start.to_usize()..line_span.end.to_usize())
             .expect("invalid line boundaries: invalid utf-8");
-        if line_src.len() < column_index {
-            return None;
-        }
-        let (pre, _) = line_src.split_at(column_index);
-        let start = line_span.start;
-        Some(start + ByteOffset::from_str_len(pre))
+
+        let content = line_src
+            .strip_suffix("\r\n")
+            .or_else(|| line_src.strip_suffix('\n'))
+            .unwrap_or(line_src);
+
+        // Include the end-of-content position as the final boundary.
+        let byte_len = content
+            .char_indices()
+            .map(|(offset, _)| offset)
+            .chain(core::iter::once(content.len()))
+            .nth(column_index)?;
+
+        Some(line_span.start + ByteOffset(byte_len as i64))
     }
 
     /// Get a [FileLineCol] corresponding to the line/column in this file at which `byte_index`
@@ -1546,4 +1557,77 @@ end
             "line4\n".as_bytes()
         );
     }
+
+    #[test]
+    fn source_content_line_column_to_offset_multibyte_utf8() {
+        // "héllo\n": h(1 byte) é(2 bytes) l l o(1 byte each) \n(1 byte).
+        const CONTENT: &str = "héllo\n";
+        let content = SourceContent::new("text", "test.txt", CONTENT);
+
+        let expected = [(0, 0u32), (1, 1), (2, 3), (3, 4), (4, 5), (5, 6)];
+        for (column, expected_byte) in expected {
+            let offset = content
+                .line_column_to_offset(LineIndex(0), ColumnIndex(column))
+                .unwrap_or_else(|| panic!("column {column} should be in bounds"));
+            assert_eq!(offset.to_u32(), expected_byte, "wrong byte offset for column {column}");
+        }
+
+        for (column, _) in expected {
+            let offset = content.line_column_to_offset(LineIndex(0), ColumnIndex(column)).unwrap();
+            let loc = content.location(offset).unwrap();
+            assert_eq!(
+                ColumnIndex::from(loc.column).to_u32(),
+                column,
+                "round-trip mismatch at column {column}"
+            );
+        }
+    }
+
+    #[test]
+    fn source_content_line_column_to_offset_rejects_line_terminator() {
+        let lf = SourceContent::new("text", "test.txt", "ab\ncd");
+        assert!(lf.line_column_to_offset(LineIndex(0), ColumnIndex(2)).is_some());
+        assert!(lf.line_column_to_offset(LineIndex(0), ColumnIndex(3)).is_none());
+
+        let crlf = SourceContent::new("text", "test.txt", "ab\r\ncd");
+        assert!(crlf.line_column_to_offset(LineIndex(0), ColumnIndex(2)).is_some());
+        assert!(crlf.line_column_to_offset(LineIndex(0), ColumnIndex(3)).is_none());
+        assert!(crlf.line_column_to_offset(LineIndex(0), ColumnIndex(4)).is_none());
+    }
+
+    #[test]
+    fn source_content_line_column_to_offset_astral_character() {
+        // U+1F600 is 1 Unicode scalar value / char, 2 UTF-16 code units, 4 bytes in UTF-8.
+        const CONTENT: &str = "\u{1F600}x";
+        let content = SourceContent::new("text", "test.txt", CONTENT);
+
+        assert_eq!(
+            content.line_column_to_offset(LineIndex(0), ColumnIndex(0)).unwrap().to_u32(),
+            0
+        );
+        assert_eq!(
+            content.line_column_to_offset(LineIndex(0), ColumnIndex(1)).unwrap().to_u32(),
+            4
+        );
+        assert_eq!(
+            content.line_column_to_offset(LineIndex(0), ColumnIndex(2)).unwrap().to_u32(),
+            5
+        );
+    }
+
+    #[test]
+    fn source_content_update_rejects_same_line_selection_spanning_line_terminator() {
+        let mut content = SourceContent::new("text", "test.txt", "a\nb");
+        assert_eq!(content.line_count(), 2);
+
+        let selection = Selection::new(Position::new(0, 1), Position::new(0, 2));
+        let result = content.update(String::new(), Some(selection), 1);
+
+        assert!(
+            result.is_err(),
+            "expected the same-line selection spanning the line terminator to be rejected, got: \
+             {result:?}"
+        );
+        assert_eq!(content.line_count(), 2);
+    }
 }
```

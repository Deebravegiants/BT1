# [?] blockifier: fix ErrorStack::Display UTF-8 char-boundary panic (#14463)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2026-06-11
Source: https://github.com/starkware-libs/sequencer/commit/3a2b8727837d3c25ca1faaa9dd658567a1c8ef90
Type: security-commit

## Details
blockifier: fix ErrorStack::Display UTF-8 char-boundary panic (#14463)

ErrorStack::Display trims over-long traces by keeping a head slice
([..TRACE_LENGTH_CAP/2]) and a tail slice ([len - TRACE_LENGTH_CAP/2..]),
using raw byte indices. Rust str slicing panics if an index isn't a char
boundary, so any multi-byte UTF-8 character straddling either cut point
panics the formatter. Trace content includes contract/VM-controlled
strings (revert reasons, VM error attributes), so this is reachable from
external input.

Snap both cut points to char boundaries via floor_char_boundary /
ceil_char_boundary helpers (the std equivalents are still unstable),
mirroring the char-safe truncation already used by Cairo1RevertSummary.

Add a regression test (head and tail cut-point cases) that places a 2-byte
'é' straddling each cut point; it panics on the old byte-slice code and
passes on the fix.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### crates/blockifier/src/execution/stack_trace.rs
```diff
@@ -168,18 +168,42 @@ impl Display for ErrorStack {
         let error_stack_str = self.stack.iter().map(String::from).join("\n");
 
         // When the trace string is too long, trim it in a way that keeps both the beginning and
-        // end.
+        // end. The cut points are snapped to char boundaries: trace content includes
+        // contract/VM-controlled strings (revert reasons, error attributes), so a multi-byte
+        // UTF-8 character straddling a raw byte index would panic the formatter.
         let final_str = if error_stack_str.len() > TRACE_LENGTH_CAP + TRACE_EXTRA_CHARS_SLACK {
-            error_stack_str[..(TRACE_LENGTH_CAP / 2)].to_string()
-                + "\n\n...\n\n"
-                + &error_stack_str[(error_stack_str.len() - TRACE_LENGTH_CAP / 2)..]
+            let half_cap = TRACE_LENGTH_CAP / 2;
+            let head_end = floor_char_boundary(&error_stack_str, half_cap);
+            let tail_start = ceil_char_boundary(&error_stack_str, error_stack_str.len() - half_cap);
+            error_stack_str[..head_end].to_string() + "\n\n...\n\n" + &error_stack_str[tail_start..]
         } else {
             error_stack_str
         };
         write!(f, "{}{}", self.header, final_str)
     }
 }
 
+/// Returns the largest index `<= idx` that lies on a `char` boundary of `s` (or `s.len()` if `idx`
+/// is past the end). Replacement for the unstable `str::floor_char_boundary`.
+fn floor_char_boundary(s: &str, mut idx: usize) -> usize {
+    if idx >= s.len() {
+        return s.len();
+    }
+    while !s.is_char_boundary(idx) {
+        idx -= 1;
+    }
+    idx
+}
+
+/// Returns the smallest index `>= idx` that lies on a `char` boundary of `s` (or `s.len()` if no
+/// such index exists below the end). Replacement for the unstable `str::ceil_char_boundary`.
+fn ceil_char_boundary(s: &str, mut idx: usize) -> usize {
+    while idx < s.len() && !s.is_char_boundary(idx) {
+        idx += 1;
+    }
+    idx
+}
+
 impl ErrorStack {
     pub fn push(&mut self, frame: ErrorStackSegment) {
         self.stack.push(frame);
```

### crates/blockifier/src/execution/stack_trace_test.rs
```diff
@@ -49,7 +49,10 @@ use crate::execution::stack_trace::{
     gen_tx_execution_error_trace,
     Cairo1RevertHeader,
     Cairo1RevertSummary,
+    ErrorStack,
+    ErrorStackSegment,
     MIN_CAIRO1_FRAME_LENGTH,
+    TRACE_EXTRA_CHARS_SLACK,
     TRACE_LENGTH_CAP,
 };
 use crate::execution::syscalls::hint_processor::ENTRYPOINT_FAILED_ERROR_FELT;
@@ -1241,3 +1244,37 @@ fn test_cairo_steps_frame_keeps_vm_exception_block_under_either_policy(
         "CairoSteps-mode revert (strip={strip}) must include `Cairo traceback` (got: {rendered:?})"
     );
 }
+
+/// `ErrorStack::Display` trims over-long traces by keeping a head slice (`[..TRACE_LENGTH_CAP /
+/// 2]`) and a tail slice (`[len - TRACE_LENGTH_CAP / 2..]`). Trace content includes
+/// contract/VM-controlled strings, so a multi-byte UTF-8 character straddling either cut point must
+/// not panic the formatter. Each case puts a 2-byte 'é' straddling exactly one of the two cut
+/// points.
+#[rstest]
+// Head cut is at byte `TRACE_LENGTH_CAP / 2`.
+#[case::head_boundary(TRACE_LENGTH_CAP / 2)]
+// Tail cut is at byte `total_len - TRACE_LENGTH_CAP / 2`.
+#[case::tail_boundary(3 * TRACE_LENGTH_CAP - TRACE_LENGTH_CAP / 2)]
+fn error_stack_display_handles_utf8_boundary(#[case] cut_point: usize) {
+    // Single frame of `total_len` bytes (well past the trim threshold) with a 2-byte 'é' starting
+    // one byte before `cut_point`, so the byte at `cut_point` is mid-character. On the buggy raw
+    // byte-slice implementation, slicing at `cut_point` panics.
+    let total_len = 3 * TRACE_LENGTH_CAP;
+    assert!(total_len > TRACE_LENGTH_CAP + TRACE_EXTRA_CHARS_SLACK);
+    let mut content = "a".repeat(cut_point - 1);
+    content.push('é');
+    content.push_str(&"b".repeat(total_len - cut_point - 1));
+    assert_eq!(content.len(), total_len);
+
+    let mut stack = ErrorStack::default();
+    stack.push(ErrorStackSegment::StringFrame(content));
+
+    // Must not panic, and must actually be trimmed (head + separator + tail).
+    let rendered = format!("{stack}");
+    assert!(rendered.contains("\n\n...\n\n"), "expected the trimmed trace to contain a separator");
+    assert!(
+        rendered.len() < TRACE_LENGTH_CAP + TRACE_EXTRA_CHARS_SLACK + 100,
+        "trimmed trace is unexpectedly long: {} bytes",
+        rendered.len()
+    );
+}
```

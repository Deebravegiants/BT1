# [?] Fix tuple codec helpers to avoid LSP stack overflows (#7611)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/sway
Published: 2026-05-04
Source: https://github.com/FuelLabs/sway/commit/c53e7e0cb9183f5ef09c14d4eba94ef4f7e284ce
Type: security-commit

## Details
Fix tuple codec helpers to avoid LSP stack overflows (#7611)

## Summary

I reproduced an LSP crash where opening and incrementally editing
`fuel-o2-exports/contracts/order-book/src/main.sw` could abort the
server and leave stale semantic highlighting behind in the client.

Daniel pointed out that the generated tuple helpers in `std::codec` are
emitted as one large left-associative `&&` chain. This change fixes the
root recursion pressure there instead of carrying the LSP stack-size
workaround.

The generator change is in `sway-lib-std/generate.sh`, and the
regenerated output is checked in at `sway-lib-std/src/codec.sw`. The
snapshot updates are included because the generated helper shape changes
source spans, IR local numbering, bytecode size, and a few gas values in
the affected e2e snapshot outputs.

## Root cause

The LSP crash was a stack overflow while processing generated
`std::codec` tuple code. The tuple triviality helpers were emitted as
deeply left-associated `&&` expressions, e.g. one expression chaining
checks across all tuple elements.

Because `&&` is left-associative, that produces a deeply left-leaning
AST. Recursive compiler and LSP passes then consume one stack frame per
node while lowering, traversing, or building semantic-token state. On
the `fuel-o2-exports` order-book repro, that was enough to bring down
the language server and leave stale semantic highlighting in the editor.

The earlier LSP stack-size mitigation kept the process alive by giving
those recursive paths more stack. Daniel's suggestion fixes the
source-level shape that was creating the stack pressure in the first
place.

## Why this mitigates it

The tuple helpers now use:

```sway
let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
let r = r && is_encode_trivial::<A>();
let r = r && is_encode_trivial::<B>();
r
```

instead of one large chained expression.

That keeps each expression shallow, so compiler and LSP recursion does
not scale with the full tuple arity in a single left-deep AST. The
language server no longer needs the stack-size workaround for this
repro.

## Validation

- regenerated `sway-lib-std/src/codec.sw` from
`sway-lib-std/generate.sh`
- verified regeneration produced no extra generated-file diff beyond the
checked-in `codec.sw`
- verified no generated left-deep tuple triviality chains remain
- `RUSTUP_TOOLCHAIN=1.93.0 cargo build -p forc-lsp --release`
- tested in an isolated VS Code session using the rebuilt
`target/release/forc-lsp`
- opened `fuel-o2-exports/contracts/order-book/src/main.sw`
- exercised the original edit/semantic-highlighting path
- observed `225` `textDocument/didChange` notifications and `11`
`textDocument/semanticTokens/range` requests
- no panic, stack overflow, abort, server exit, or stale-highlighting
failure reproduced
- updated the affected e2e `stdout.snap` files after CI snapshot drift
- `RUSTUP_TOOLCHAIN=1.93.0 cargo run --locked --release --bin test --
--locked --kind snapshot`

## Patch
### sway-lib-std/generate.sh
```diff
@@ -1,12 +1,24 @@
 #! /bin/bash
 
+# Use GNU sed (`gsed` on macOS via `brew install gnu-sed`); BSD sed in-place
+# semantics differ and break the substitutions below.
+SED=${SED:-sed}
+if ! $SED --version >/dev/null 2>&1; then
+    if command -v gsed >/dev/null 2>&1; then
+        SED=gsed
+    else
+        echo "GNU sed is required (install with 'brew install gnu-sed' on macOS)." >&2
+        exit 1
+    fi
+fi
+
 # Needs to exist at least one line between them
 remove_generated_code() {
     START=`grep -n "BEGIN $1" ./src/$2`
     START=${START%:*}
     END=`grep -n "END $1" ./src/$2`
     END=${END%:*}
-    sed -i "$((START+1)),$((END-1))d" ./src/$2
+    $SED -i "$((START+1)),$((END-1))d" ./src/$2
 }
 
 generate_tuple_encode() {
@@ -32,13 +44,17 @@ generate_tuple_encode() {
         CODE="$CODE $element: AbiEncode, "
     done
 
+    # Emit the body as a sequence of `let r = r && ...;` statements rather
+    # than one giant left-deep `&&` chain. Long chains produce a deeply
+    # left-leaning AST that drives recursive compiler / LSP transforms into
+    # stack overflows on real-world tuples.
     ISTRIVIAL=""
     for element in ${elements[@]}
     do
-        ISTRIVIAL="$ISTRIVIAL \&\& is_encode_trivial::<$element>()"
+        ISTRIVIAL="$ISTRIVIAL let r = r \&\& is_encode_trivial::<$element>();"
     done
 
-    CODE="$CODE{ fn is_encode_trivial() -> bool { __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() $ISTRIVIAL } fn abi_encode(self, buffer: Buffer) -> Buffer { "
+    CODE="$CODE{ fn is_encode_trivial() -> bool { let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>(); $ISTRIVIAL r } fn abi_encode(self, buffer: Buffer) -> Buffer { "
 
     i=0
     for element in ${elements[@]}
@@ -49,7 +65,7 @@ generate_tuple_encode() {
 
     CODE="$CODE buffer } }"
 
-    sed -i "s/\/\/ BEGIN TUPLES_ENCODE/\/\/ BEGIN TUPLES_ENCODE\n$CODE/g" ./src/codec.sw
+    $SED -i "s/\/\/ BEGIN TUPLES_ENCODE/\/\/ BEGIN TUPLES_ENCODE\n$CODE/g" ./src/codec.sw
 }
 
 remove_generated_code "TUPLES_ENCODE" "codec.sw"
@@ -103,13 +119,17 @@ generate_tuple_decode() {
         CODE="$CODE $element: AbiDecode, "
     done
 
+    # Emit the body as a sequence of `let r = r && ...;` statements rather
+    # than one giant left-deep `&&` chain. Long chains produce a deeply
+    # left-leaning AST that drives recursive compiler / LSP transforms into
+    # stack overflows on real-world tuples.
     ISTRIVIAL=""
     for element in ${elements[@]}
     do
-        ISTRIVIAL="$ISTRIVIAL \&\& is_decode_trivial::<$element>()"
+        ISTRIVIAL="$ISTRIVIAL let r = r \&\& is_decode_trivial::<$element>();"
     done
 
-    CODE="$CODE{ fn is_decode_trivial() -> bool { __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() $ISTRIVIAL } fn abi_decode(ref mut buffer: BufferReader) -> Self { ("
+    CODE="$CODE{ fn is_decode_trivial() -> bool { let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>(); $ISTRIVIAL r } fn abi_decode(ref mut buffer: BufferReader) -> Self { ("
 
     for element in ${elements[@]}
     do
@@ -118,7 +138,7 @@ generate_tuple_decode() {
 
     CODE="$CODE) } }"
 
-    sed -i "s/\/\/ BEGIN TUPLES_DECODE/\/\/ BEGIN TUPLES_DECODE\n$CODE/g" ./src/codec.sw
+    $SED -i "s/\/\/ BEGIN TUPLES_DECODE/\/\/ BEGIN TUPLES_DECODE\n$CODE/g" ./src/codec.sw
 }
 
 remove_generated_code "TUPLES_DECODE" "codec.sw"
@@ -183,7 +203,7 @@ generate_tuple_debug() {
 
     CODE="$CODE f.finish(); } }"
 
-    sed -i "s/\/\/ BEGIN TUPLES_DEBUG/\/\/ BEGIN TUPLES_DEBUG\n$CODE/g" ./src/debug.sw
+    $SED -i "s/\/\/ BEGIN TUPLES_DEBUG/\/\/ BEGIN TUPLES_DEBUG\n$CODE/g" ./src/debug.sw
 }
 
 remove_generated_code "TUPLES_DEBUG" "debug.sw"
```

### sway-lib-std/src/codec.sw
```diff
@@ -344,7 +344,9 @@ where
     A: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -357,7 +359,10 @@ where
     B: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -372,7 +377,11 @@ where
     C: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -389,7 +398,12 @@ where
     D: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -408,7 +422,13 @@ where
     E: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -429,7 +449,14 @@ where
     F: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -452,7 +479,15 @@ where
     G: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -477,7 +512,16 @@ where
     H: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -504,7 +548,17 @@ where
     I: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -533,7 +587,18 @@ where
     J: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -564,7 +629,19 @@ where
     K: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -597,7 +674,20 @@ where
     L: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -632,7 +722,21 @@ where
     M: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -669,7 +773,22 @@ where
     N: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -708,7 +827,23 @@ where
     O: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -749,7 +884,24 @@ where
     P: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -792,7 +944,25 @@ where
     Q: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -837,7 +1007,26 @@ where
     R: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -884,7 +1073,27 @@ where
     S: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -933,7 +1142,28 @@ where
     T: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -984,7 +1214,29 @@ where
     U: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1037,7 +1289,30 @@ where
     V: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>() && is_encode_trivial::<V>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        let r = r && is_encode_trivial::<V>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1092,7 +1367,31 @@ where
     W: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>() && is_encode_trivial::<V>() && is_encode_trivial::<W>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        let r = r && is_encode_trivial::<V>();
+        let r = r && is_encode_trivial::<W>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1149,7 +1448,32 @@ where
     X: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>() && is_encode_trivial::<V>() && is_encode_trivial::<W>() && is_encode_trivial::<X>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        let r = r && is_encode_trivial::<V>();
+        let r = r && is_encode_trivial::<W>();
+        let r = r && is_encode_trivial::<X>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1208,7 +1532,33 @@ where
     Y: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>() && is_encode_trivial::<V>() && is_encode_trivial::<W>() && is_encode_trivial::<X>() && is_encode_trivial::<Y>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        let r = r && is_encode_trivial::<V>();
+        let r = r && is_encode_trivial::<W>();
+        let r = r && is_encode_trivial::<X>();
+        let r = r && is_encode_trivial::<Y>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1269,7 +1619,34 @@ where
     Z: AbiEncode,
 {
     fn is_encode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_encode_trivial::<A>() && is_encode_trivial::<B>() && is_encode_trivial::<C>() && is_encode_trivial::<D>() && is_encode_trivial::<E>() && is_encode_trivial::<F>() && is_encode_trivial::<G>() && is_encode_trivial::<H>() && is_encode_trivial::<I>() && is_encode_trivial::<J>() && is_encode_trivial::<K>() && is_encode_trivial::<L>() && is_encode_trivial::<M>() && is_encode_trivial::<N>() && is_encode_trivial::<O>() && is_encode_trivial::<P>() && is_encode_trivial::<Q>() && is_encode_trivial::<R>() && is_encode_trivial::<S>() && is_encode_trivial::<T>() && is_encode_trivial::<U>() && is_encode_trivial::<V>() && is_encode_trivial::<W>() && is_encode_trivial::<X>() && is_encode_trivial::<Y>() && is_encode_trivial::<Z>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_encode_trivial::<A>();
+        let r = r && is_encode_trivial::<B>();
+        let r = r && is_encode_trivial::<C>();
+        let r = r && is_encode_trivial::<D>();
+        let r = r && is_encode_trivial::<E>();
+        let r = r && is_encode_trivial::<F>();
+        let r = r && is_encode_trivial::<G>();
+        let r = r && is_encode_trivial::<H>();
+        let r = r && is_encode_trivial::<I>();
+        let r = r && is_encode_trivial::<J>();
+        let r = r && is_encode_trivial::<K>();
+        let r = r && is_encode_trivial::<L>();
+        let r = r && is_encode_trivial::<M>();
+        let r = r && is_encode_trivial::<N>();
+        let r = r && is_encode_trivial::<O>();
+        let r = r && is_encode_trivial::<P>();
+        let r = r && is_encode_trivial::<Q>();
+        let r = r && is_encode_trivial::<R>();
+        let r = r && is_encode_trivial::<S>();
+        let r = r && is_encode_trivial::<T>();
+        let r = r && is_encode_trivial::<U>();
+        let r = r && is_encode_trivial::<V>();
+        let r = r && is_encode_trivial::<W>();
+        let r = r && is_encode_trivial::<X>();
+        let r = r && is_encode_trivial::<Y>();
+        let r = r && is_encode_trivial::<Z>();
+        r
     }
     fn abi_encode(self, buffer: Buffer) -> Buffer {
         let buffer = self.0.abi_encode(buffer);
@@ -1580,7 +1957,9 @@ where
     A: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (A::abi_decode(buffer), )
@@ -1592,7 +1971,10 @@ where
     B: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (A::abi_decode(buffer), B::abi_decode(buffer))
@@ -1605,7 +1987,11 @@ where
     C: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (A::abi_decode(buffer), B::abi_decode(buffer), C::abi_decode(buffer))
@@ -1619,7 +2005,12 @@ where
     D: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1639,7 +2030,13 @@ where
     E: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1661,7 +2058,14 @@ where
     F: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1685,7 +2089,15 @@ where
     G: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1711,7 +2123,16 @@ where
     H: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1739,7 +2160,17 @@ where
     I: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1769,7 +2200,18 @@ where
     J: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1801,7 +2243,19 @@ where
     K: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1835,7 +2289,20 @@ where
     L: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1871,7 +2338,21 @@ where
     M: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1909,7 +2390,22 @@ where
     N: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1949,7 +2445,23 @@ where
     O: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -1991,7 +2503,24 @@ where
     P: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2035,7 +2564,25 @@ where
     Q: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2081,7 +2628,26 @@ where
     R: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2129,7 +2695,27 @@ where
     S: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2179,7 +2765,28 @@ where
     T: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2231,7 +2838,29 @@ where
     U: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2285,7 +2914,30 @@ where
     V: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>() && is_decode_trivial::<V>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        let r = r && is_decode_trivial::<V>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2341,7 +2993,31 @@ where
     W: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>() && is_decode_trivial::<V>() && is_decode_trivial::<W>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        let r = r && is_decode_trivial::<V>();
+        let r = r && is_decode_trivial::<W>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2399,7 +3075,32 @@ where
     X: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>() && is_decode_trivial::<V>() && is_decode_trivial::<W>() && is_decode_trivial::<X>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        let r = r && is_decode_trivial::<V>();
+        let r = r && is_decode_trivial::<W>();
+        let r = r && is_decode_trivial::<X>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2459,7 +3160,33 @@ where
     Y: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>() && is_decode_trivial::<V>() && is_decode_trivial::<W>() && is_decode_trivial::<X>() && is_decode_trivial::<Y>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        let r = r && is_decode_trivial::<V>();
+        let r = r && is_decode_trivial::<W>();
+        let r = r && is_decode_trivial::<X>();
+        let r = r && is_decode_trivial::<Y>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
@@ -2521,7 +3248,34 @@ where
     Z: AbiDecode,
 {
     fn is_decode_trivial() -> bool {
-        __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>() && is_decode_trivial::<A>() && is_decode_trivial::<B>() && is_decode_trivial::<C>() && is_decode_trivial::<D>() && is_decode_trivial::<E>() && is_decode_trivial::<F>() && is_decode_trivial::<G>() && is_decode_trivial::<H>() && is_decode_trivial::<I>() && is_decode_trivial::<J>() && is_decode_trivial::<K>() && is_decode_trivial::<L>() && is_decode_trivial::<M>() && is_decode_trivial::<N>() && is_decode_trivial::<O>() && is_decode_trivial::<P>() && is_decode_trivial::<Q>() && is_decode_trivial::<R>() && is_decode_trivial::<S>() && is_decode_trivial::<T>() && is_decode_trivial::<U>() && is_decode_trivial::<V>() && is_decode_trivial::<W>() && is_decode_trivial::<X>() && is_decode_trivial::<Y>() && is_decode_trivial::<Z>()
+        let r = __runtime_mem_id::<Self>() == __encoding_mem_id::<Self>();
+        let r = r && is_decode_trivial::<A>();
+        let r = r && is_decode_trivial::<B>();
+        let r = r && is_decode_trivial::<C>();
+        let r = r && is_decode_trivial::<D>();
+        let r = r && is_decode_trivial::<E>();
+        let r = r && is_decode_trivial::<F>();
+        let r = r && is_decode_trivial::<G>();
+        let r = r && is_decode_trivial::<H>();
+        let r = r && is_decode_trivial::<I>();
+        let r = r && is_decode_trivial::<J>();
+        let r = r && is_decode_trivial::<K>();
+        let r = r && is_decode_trivial::<L>();
+        let r = r && is_decode_trivial::<M>();
+        let r = r && is_decode_trivial::<N>();
+        let r = r && is_decode_trivial::<O>();
+        let r = r && is_decode_trivial::<P>();
+        let r = r && is_decode_trivial::<Q>();
+        let r = r && is_decode_trivial::<R>();
+        let r = r && is_decode_trivial::<S>();
+        let r = r && is_decode_trivial::<T>();
+        let r = r && is_decode_trivial::<U>();
+        let r = r && is_decode_trivial::<V>();
+        let r = r && is_decode_trivial::<W>();
+        let r = r && is_decode_trivial::<X>();
+        let r = r && is_decode_trivial::<Y>();
+        let r = r && is_decode_trivial::<Z>();
+        r
     }
     fn abi_decode(ref mut buffer: BufferReader) -> Self {
         (
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/array/array_repeat/stdout.snap
```diff
@@ -458,8 +458,8 @@ script {
 !108 = span !10 3147 3171
 !109 = fn_call_path_span !10 3147 3157
 !110 = "test/src/e2e_vm_tests/reduced_std_libs/sway-lib-std-assert/src/codec.sw"
-!111 = span !110 49688 49698
-!112 = fn_call_path_span !110 49693 49696
+!111 = span !110 56851 56861
+!112 = fn_call_path_span !110 56856 56859
 !113 = "test/src/e2e_vm_tests/reduced_std_libs/sway-lib-std-assert/src/raw_slice.sw"
 !114 = span !113 2922 2926
 !115 = (!108 !109 !111 !112 !114)
@@ -471,10 +471,10 @@ script {
 !121 = (!108 !109 !111 !112)
 !122 = span !113 2928 2929
 !123 = (!108 !109 !111 !112 !122)
-!124 = span !110 49667 49782
+!124 = span !110 56830 56945
 !125 = (!108 !109 !124)
-!126 = span !110 49714 49723
-!127 = span !110 49737 49752
+!126 = span !110 56877 56886
+!127 = span !110 56900 56915
 !128 = span !10 3192 3320
 !129 = fn_name_span !10 3195 3203
 !130 = (!128 !129 !48)
@@ -496,7 +496,7 @@ script {
 !146 = fn_name_span !143 584 587
 !147 = (!145 !146)
 !148 = span !143 642 647
-!149 = span !110 48850 48862
+!149 = span !110 56013 56025
 !150 = (!148 !149)
 !151 = (!148 !149)
 !152 = (!148 !149)
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/configurable_dedup_decode/stdout.snap
```diff
@@ -18,52 +18,52 @@ script {
 
     pub fn abi_decode_in_place_0(ptr !4: ptr, len !5: u64, target !6: ptr) -> (), !9 {
         entry(ptr: ptr, len: u64, target: ptr):
-        v138v1 = asm(src: ptr, target: target, len: len) -> (), !10 {
+        v146v1 = asm(src: ptr, target: target, len: len) -> (), !10 {
             mcp    target src len, !11
         }
-        v216v1 = const unit ()
-        ret () v216v1
+        v224v1 = const unit ()
+        ret () v224v1
     }
 
     pub entry fn __entry() -> __ptr never, !15 {
         local u64 _result
 
         entry():
-        v308v1 = call main_15(), !18
-        v309v1 = get_local __ptr u64, _result, !19
-        store v308v1 to v309v1, !19
-        v328v1 = get_local __ptr u64, _result, !20
-        v319v1 = const u64 8
-        retd v328v1 v319v1, !24
+        v316v1 = call main_15(), !18
+        v317v1 = get_local __ptr u64, _result, !19
+        store v316v1 to v317v1, !19
+        v336v1 = get_local __ptr u64, _result, !20
+        v327v1 = const u64 8
+        retd v336v1 v327v1, !24
     }
 
     entry_orig fn main_15() -> u64, !27 {
         entry():
-        v298v1 = get_config __ptr { u64 }, WRAPPED, !28
-        v299v1 = const u64 0
-        v300v1 = get_elem_ptr v298v1, __ptr u64, v299v1, !29
-        v301v1 = load v300v1
-        v302v1 = get_config __ptr { u64 }, TUPLE, !30
-        v303v1 = const u64 0
-        v304v1 = get_elem_ptr v302v1, __ptr u64, v303v1, !31
-        v305v1 = load v304v1
-        v462v1 = add v301v1, v305v1, !34
-        ret u64 v462v1
+        v306v1 = get_config __ptr { u64 }, WRAPPED, !28
+        v307v1 = const u64 0
+        v308v1 = get_elem_ptr v306v1, __ptr u64, v307v1, !29
+        v309v1 = load v308v1
+        v310v1 = get_config __ptr { u64 }, TUPLE, !30
+        v311v1 = const u64 0
+        v312v1 = get_elem_ptr v310v1, __ptr u64, v311v1, !31
+        v313v1 = load v312v1
+        v502v1 = add v309v1, v313v1, !34
+        ret u64 v502v1
     }
 }
 
 !0 = "test/src/e2e_vm_tests/test_programs/should_pass/language/configurable_dedup_decode/src/main.sw"
 !1 = span !0 177 182
 !2 = span !0 136 143
 !3 = "sway-lib-std/src/codec.sw"
-!4 = span !3 49961 49964
-!5 = span !3 49975 49978
-!6 = span !3 49985 49991
-!7 = span !3 49931 50445
-!8 = fn_name_span !3 49938 49957
+!4 = span !3 57124 57127
+!5 = span !3 57138 57141
+!6 = span !3 57148 57154
+!7 = span !3 57094 57608
+!8 = fn_name_span !3 57101 57120
 !9 = (!7 !8)
-!10 = span !3 50070 50153
-!11 = span !3 50124 50142
+!10 = span !3 57233 57316
+!11 = span !3 57287 57305
 !12 = "test/src/e2e_vm_tests/test_programs/should_pass/language/configurable_dedup_decode/src/main.<autogenerated>.sw"
 !13 = span !12 0 131
 !14 = fn_name_span !12 7 14
@@ -75,7 +75,7 @@ script {
 !20 = span !12 109 116
 !21 = span !12 83 117
 !22 = fn_call_path_span !12 83 100
-!23 = span !3 49161 49187
+!23 = span !3 56324 56350
 !24 = (!21 !22 !23)
 !25 = span !0 202 246
 !26 = fn_name_span !0 205 209
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/const_generics/stdout.snap
```diff
@@ -71,7 +71,7 @@ warning
 ____
 
   Compiled script "const_generics" with 2 warnings.
-    Finished debug [unoptimized + fuel] target(s) [8.68 KB] in ???
+    Finished debug [unoptimized + fuel] target(s) [8.712 KB] in ???
      Running 1 test, filtered 0 tests
 
 tested -- const_generics
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/logging/stdout.snap
```diff
@@ -1125,7 +1125,7 @@ script {
 !9 = span !0 83 117
 !10 = fn_call_path_span !0 83 100
 !11 = "test/src/e2e_vm_tests/reduced_std_libs/sway-lib-std-vec/src/codec.sw"
-!12 = span !11 49161 49187
+!12 = span !11 56324 56350
 !13 = (!9 !10 !12)
 !14 = "test/src/e2e_vm_tests/test_programs/should_pass/language/logging/src/main.sw"
 !15 = span !14 594 999
@@ -1193,7 +1193,7 @@ script {
 !77 = inline "never"
 !78 = (!75 !76 !77)
 !79 = span !14 584 588
-!80 = span !11 48850 48862
+!80 = span !11 56013 56025
 !81 = (!79 !80)
 !82 = (!79 !80)
 !83 = (!79 !80)
@@ -1281,8 +1281,8 @@ script {
 !165 = fn_call_path_span !24 6194 6196
 !166 = (!164 !165)
 !167 = (!75 !76 !77)
-!168 = span !11 48742 48766
-!169 = fn_call_path_span !11 48742 48759
+!168 = span !11 55905 55929
+!169 = fn_call_path_span !11 55905 55922
 !170 = span !11 3637 3659
 !171 = fn_call_path_span !11 3637 3657
 !172 = span !0 148 205
@@ -1311,8 +1311,8 @@ script {
 !195 = (!79 !80)
 !196 = (!79 !80)
 !197 = (!79 !80)
-!198 = span !11 48898 48931
-!199 = fn_call_path_span !11 48906 48916
+!198 = span !11 56061 56094
+!199 = fn_call_path_span !11 56069 56079
 !200 = (!79 !198 !199)
 !201 = (!79 !198 !199)
 !202 = span !0 556 560
@@ -1602,9 +1602,9 @@ script {
 !486 = (!79 !198 !199 !485)
 !487 = span !0 840 846
 !488 = (!79 !198 !199 !487)
-!489 = span !11 48885 48932
+!489 = span !11 56048 56095
 !490 = (!79 !489)
-!491 = span !11 48941 48947
+!491 = span !11 56104 56110
 !492 = (!79 !491)
 !493 = (!79 !198 !199 !448 !449)
 !494 = (!79 !198 !199 !448 !449)
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_one_u64/stdout.snap
```diff
@@ -30,31 +30,31 @@ script {
         local { u64 } args
 
         entry():
-        v104v1 = const u64 0, !5
-        v364v1 = gtf v104v1, 10, !11
-        v365v1 = bitcast v364v1 to ptr, !12
-        v418v1 = cast_ptr v365v1 to __ptr { u64 }, !15
-        v432v1 = get_local __ptr { u64 }, __aggr_memcpy_0
-        mem_copy_val v432v1, v418v1
-        v112v1 = get_local __ptr { u64 }, args, !16
-        mem_copy_val v112v1, v432v1
-        v134v1 = get_local __ptr { u64 }, args, !17
-        v135v1 = const u64 0
-        v136v1 = get_elem_ptr v134v1, __ptr u64, v135v1, !18
-        v137v1 = load v136v1
-        v138v1 = call main_11(v137v1), !21
-        v139v1 = get_local __ptr u64, _result, !22
-        store v138v1 to v139v1, !22
-        v158v1 = get_local __ptr u64, _result, !23
-        v149v1 = const u64 8
-        retd v158v1 v149v1, !27
+        v112v1 = const u64 0, !5
+        v384v1 = gtf v112v1, 10, !11
+        v385v1 = bitcast v384v1 to ptr, !12
+        v442v1 = cast_ptr v385v1 to __ptr { u64 }, !15
+        v456v1 = get_local __ptr { u64 }, __aggr_memcpy_0
+        mem_copy_val v456v1, v442v1
+        v120v1 = get_local __ptr { u64 }, args, !16
+        mem_copy_val v120v1, v456v1
+        v142v1 = get_local __ptr { u64 }, args, !17
+        v143v1 = const u64 0
+        v144v1 = get_elem_ptr v142v1, __ptr u64, v143v1, !18
+        v145v1 = load v144v1
+        v146v1 = call main_11(v145v1), !21
+        v147v1 = get_local __ptr u64, _result, !22
+        store v146v1 to v147v1, !22
+        v166v1 = get_local __ptr u64, _result, !23
+        v157v1 = const u64 8
+        retd v166v1 v157v1, !27
     }
 
     entry_orig fn main_11(baba !29: u64) -> u64, !32 {
         entry(baba: u64):
-        v131v1 = const u64 1, !33
-        v350v1 = add baba, v131v1, !36
-        ret u64 v350v1
+        v139v1 = const u64 1, !33
+        v370v1 = add baba, v139v1, !36
+        ret u64 v370v1
     }
 }
 
@@ -66,13 +66,13 @@ script {
 !5 = span !4 1542 1543
 !6 = span !0 59 89
 !7 = fn_call_path_span !0 59 77
-!8 = span !4 91615 91647
-!9 = fn_call_path_span !4 91615 91645
+!8 = span !4 105941 105973
+!9 = fn_call_path_span !4 105941 105971
 !10 = span !4 1525 1549
 !11 = (!6 !7 !8 !9 !10)
 !12 = (!6 !7 !8 !9 !10)
-!13 = span !4 91590 91648
-!14 = fn_call_path_span !4 91590 91609
+!13 = span !4 105916 105974
+!14 = fn_call_path_span !4 105916 105935
 !15 = (!6 !7 !13 !14)
 !16 = span !0 40 90
 !17 = span !0 131 135
@@ -84,7 +84,7 @@ script {
 !23 = span !0 182 189
 !24 = span !0 156 190
 !25 = fn_call_path_span !0 156 173
-!26 = span !4 49161 49187
+!26 = span !4 56324 56350
 !27 = (!24 !25 !26)
 !28 = "test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_one_u64/src/main.sw"
 !29 = span !28 17 21
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_ref/stdout.snap
```diff
@@ -36,6 +36,8 @@ script {
         local u64 other_0
         local ptr ptr_
         local __ptr { { u64 } } ptr__
+        local bool r
+        local bool r_
         local u64 self_
         local u64 self_0
         local __ptr { ptr } self_00
@@ -44,171 +46,179 @@ script {
         local u64 v
 
         entry():
-        v823v1 = get_local __ptr never, __ret_value
-        v131v1 = const u64 0, !5
-        v675v1 = gtf v131v1, 10, !11
-        v676v1 = bitcast v675v1 to ptr, !12
-        v678v1 = get_local __ptr ptr, ptr_, !15
-        store v676v1 to v678v1, !16
-        v680v1 = get_local __ptr u64, self_, !23
+        v863v1 = get_local __ptr never, __ret_value
+        v139v1 = const u64 0, !5
+        v707v1 = gtf v139v1, 10, !11
+        v708v1 = bitcast v707v1 to ptr, !12
+        v710v1 = get_local __ptr ptr, ptr_, !15
+        store v708v1 to v710v1, !16
+        v712v1 = get_local __ptr u64, self_, !23
         v23v1 = const u64 14333742065139216717
-        store v23v1 to v680v1, !24
-        v682v1 = get_local __ptr u64, other_, !25
+        store v23v1 to v712v1, !24
+        v714v1 = get_local __ptr u64, other_, !25
         v24v1 = const u64 14333742065139216717
-        store v24v1 to v682v1, !26
-        v684v1 = get_local __ptr u64, self_, !29
-        v685v1 = load v684v1, !30
-        v686v1 = get_local __ptr u64, other_, !32
-        v687v1 = load v686v1, !33
-        v688v1 = cmp eq v685v1 v687v1, !34
-        cbr v688v1, decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block0(), decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v688v1), !36
+        store v24v1 to v714v1, !26
+        v716v1 = get_local __ptr u64, self_, !29
+        v717v1 = load v716v1, !30
+        v718v1 = get_local __ptr u64, other_, !32
+        v719v1 = load v718v1, !33
+        v720v1 = cmp eq v717v1 v719v1, !34
+        v722v1 = get_local __ptr bool, r, !36
+        store v720v1 to v722v1, !37
+        v724v1 = get_local __ptr bool, r, !39
+        v725v1 = load v724v1, !40
+        cbr v725v1, decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block0(), decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v725v1), !42
 
         decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block0():
-        v691v1 = get_local __ptr u64, self_0, !41
-        v28v1 = const u64 17045370188297990602
-        store v28v1 to v691v1, !42
-        v693v1 = get_local __ptr u64, other_0, !43
-        v29v1 = const u64 17045370188297990602
-        store v29v1 to v693v1, !44
-        v695v1 = get_local __ptr u64, self_0, !45
-        v696v1 = load v695v1, !46
-        v697v1 = get_local __ptr u64, other_0, !47
-        v698v1 = load v697v1, !48
-        v699v1 = cmp eq v696v1 v698v1, !49
-        cbr v699v1, decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block0(), decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v699v1), !51
+        v727v1 = get_local __ptr u64, self_0, !47
+        v32v1 = const u64 17045370188297990602
+        store v32v1 to v727v1, !48
+        v729v1 = get_local __ptr u64, other_0, !49
+        v33v1 = const u64 17045370188297990602
+        store v33v1 to v729v1, !50
+        v731v1 = get_local __ptr u64, self_0, !51
+        v732v1 = load v731v1, !52
+        v733v1 = get_local __ptr u64, other_0, !53
+        v734v1 = load v733v1, !54
+        v735v1 = cmp eq v732v1 v734v1, !55
+        cbr v735v1, decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block0(), decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v735v1), !57
 
         decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block0():
-        v33v1 = const bool true, !52
-        br decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v33v1), !53
+        v37v1 = const bool true, !58
+        br decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v37v1), !59
 
-        decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v662v1: bool):
-        br decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v662v1), !54
+        decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_is_decode_trivial_5_is_decode_trivial_6_block1(v694v1: bool):
+        br decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v694v1), !60
 
-        decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v665v1: bool):
-        cbr v665v1, decode_script_data_0_decode_from_raw_ptr_1_block0(), decode_script_data_0_decode_from_raw_ptr_1_block1(), !55
+        decode_script_data_0_decode_from_raw_ptr_1_is_decode_trivial_2_is_decode_trivial_3_block1(v697v1: bool):
+        v744v1 = get_local __ptr bool, r_, !62
+        store v697v1 to v744v1, !63
+        v746v1 = get_local __ptr bool, r_, !65
+        v747v1 = load v746v1, !66
+        cbr v747v1, decode_script_data_0_decode_from_raw_ptr_1_block0(), decode_script_data_0_decode_from_raw_ptr_1_block1(), !67
 
         decode_script_data_0_decode_from_raw_ptr_1_block0():
-        v772v1 = get_local __ptr ptr, ptr_, !57
-        v773v1 = load v772v1, !58
-        v774v1 = cast_ptr v773v1 to __ptr { { u64 } }, !59
-        v775v1 = get_local __ptr __ptr { { u64 } }, ptr__, !61
-        store v774v1 to v775v1, !62
-        v777v1 = get_local __ptr __ptr { { u64 } }, ptr__, !64
-        v778v1 = load v777v1, !65
-        v804v1 = get_local __ptr { { u64 } }, __tmp_block_arg1
-        mem_copy_val v804v1, v778v1
-        br decode_script_data_0_decode_from_raw_ptr_1_block2(v804v1), !66
+        v812v1 = get_local __ptr ptr, ptr_, !69
+        v813v1 = load v812v1, !70
+        v814v1 = cast_ptr v813v1 to __ptr { { u64 } }, !71
+        v815v1 = get_local __ptr __ptr { { u64 } }, ptr__, !73
+        store v814v1 to v815v1, !74
+        v817v1 = get_local __ptr __ptr { { u64 } }, ptr__, !76
+        v818v1 = load v817v1, !77
+        v844v1 = get_local __ptr { { u64 } }, __tmp_block_arg1
+        mem_copy_val v844v1, v818v1
+        br decode_script_data_0_decode_from_raw_ptr_1_block2(v844v1), !78
 
         decode_script_data_0_decode_from_raw_ptr_1_block1():
-        v711v1 = get_local __ptr { ptr }, __struct_init_0, !68
-        v712v1 = get_local __ptr ptr, ptr_, !70
-        v193v1 = const u64 0
-        v714v1 = get_elem_ptr v711v1, __ptr ptr, v193v1, !71
-        mem_copy_val v714v1, v712v1
-        v717v1 = get_local __ptr { ptr }, buffer, !73
-        mem_copy_val v717v1, v711v1
-        v719v1 = get_local __ptr { ptr }, buffer, !75
-        v721v1 = get_local __ptr __ptr { ptr }, buffer_, !78
-        store v719v1 to v721v1, !79
-        v723v1 = get_local __ptr { { u64 } }, __tuple_init_0, !81
-        v724v1 = get_local __ptr __ptr { ptr }, buffer_, !83
-        v726v1 = get_local __ptr __ptr { ptr }, buffer_0, !86
-        mem_copy_val v726v1, v724v1
-        v728v1 = get_local __ptr { u64 }, __struct_init_00, !88
-        v729v1 = get_local __ptr __ptr { ptr }, buffer_0, !90
-        v731v1 = get_local __ptr __ptr { ptr }, self_1, !93
-        mem_copy_val v731v1, v729v1
-        v733v1 = get_local __ptr __ptr { ptr }, self_1, !95
-        v735v1 = get_local __ptr __ptr { ptr }, buffer_00, !98
-        mem_copy_val v735v1, v733v1
-        v737v1 = get_local __ptr __ptr { ptr }, buffer_00, !100
-        v739v1 = get_local __ptr __ptr { ptr }, self_00, !103
-        mem_copy_val v739v1, v737v1
-        v741v1 = get_local __ptr __ptr { ptr }, self_00, !105
-        v742v1 = load v741v1, !106
-        v81v1 = const u64 0
-        v743v1 = get_elem_ptr v742v1, __ptr ptr, v81v1, !108
-        v744v1 = load v743v1, !109
-        v745v1 = asm(ptr: v744v1, val) -> u64 val, !111 {
-            lw     val ptr i0, !112
-        }
-        v746v1 = get_local __ptr u64, v, !114
-        store v745v1 to v746v1, !115
-        v748v1 = get_local __ptr __ptr { ptr }, self_00, !117
-        v749v1 = load v748v1, !118
+        v751v1 = get_local __ptr { ptr }, __struct_init_0, !80
+        v752v1 = get_local __ptr ptr, ptr_, !82
+        v201v1 = const u64 0
+        v754v1 = get_elem_ptr v751v1, __ptr ptr, v201v1, !83
+        mem_copy_val v754v1, v752v1
+        v757v1 = get_local __ptr { ptr }, buffer, !85
+        mem_copy_val v757v1, v751v1
+        v759v1 = get_local __ptr { ptr }, buffer, !87
+        v761v1 = get_local __ptr __ptr { ptr }, buffer_, !90
+        store v759v1 to v761v1, !91
+        v763v1 = get_local __ptr { { u64 } }, __tuple_init_0, !93
+        v764v1 = get_local __ptr __ptr { ptr }, buffer_, !95
+        v766v1 = get_local __ptr __ptr { ptr }, buffer_0, !98
+        mem_copy_val v766v1, v764v1
+        v768v1 = get_local __ptr { u64 }, __struct_init_00, !100
+        v769v1 = get_local __ptr __ptr { ptr }, buffer_0, !102
+        v771v1 = get_local __ptr __ptr { ptr }, self_1, !105
+        mem_copy_val v771v1, v769v1
+        v773v1 = get_local __ptr __ptr { ptr }, self_1, !107
+        v775v1 = get_local __ptr __ptr { ptr }, buffer_00, !110
+        mem_copy_val v775v1, v773v1
+        v777v1 = get_local __ptr __ptr { ptr }, buffer_00, !112
+        v779v1 = get_local __ptr __ptr { ptr }, self_00, !115
+        mem_copy_val v779v1, v777v1
+        v781v1 = get_local __ptr __ptr { ptr }, self_00, !117
+        v782v1 = load v781v1, !118
         v89v1 = const u64 0
-        v750v1 = get_elem_ptr v749v1, __ptr ptr, v89v1, !119
-        v751v1 = load v750v1, !120
-        v87v1 = const u64 1
-        v92v1 = const u64 8, !121
-        v752v1 = mul v87v1, v92v1, !122
-        v753v1 = add v751v1, v752v1, !123
-        v754v1 = get_local __ptr __ptr { ptr }, self_00, !125
-        v755v1 = load v754v1, !126
-        v96v1 = const u64 0
-        v756v1 = get_elem_ptr v755v1, __ptr ptr, v96v1, !127
-        store v753v1 to v756v1, !128
-        v758v1 = get_local __ptr u64, v, !130
-        v759v1 = load v758v1, !131
-        v199v1 = const u64 0
-        v763v1 = get_elem_ptr v728v1, __ptr u64, v199v1, !132
-        store v759v1 to v763v1, !133
-        v796v1 = get_local __ptr { u64 }, __tmp_block_arg
-        mem_copy_val v796v1, v728v1
-        v196v1 = const u64 0
-        v767v1 = get_elem_ptr v723v1, __ptr { u64 }, v196v1, !134
-        mem_copy_val v767v1, v796v1
-        v800v1 = get_local __ptr { { u64 } }, __tmp_block_arg0
-        mem_copy_val v800v1, v723v1
-        v806v1 = get_local __ptr { { u64 } }, __tmp_block_arg1
-        mem_copy_val v806v1, v800v1
-        br decode_script_data_0_decode_from_raw_ptr_1_block2(v806v1), !135
+        v783v1 = get_elem_ptr v782v1, __ptr ptr, v89v1, !120
+        v784v1 = load v783v1, !121
+        v785v1 = asm(ptr: v784v1, val) -> u64 val, !123 {
+            lw     val ptr i0, !124
+        }
+        v786v1 = get_local __ptr u64, v, !126
+        store v785v1 to v786v1, !127
+        v788v1 = get_local __ptr __ptr { ptr }, self_00, !129
+        v789v1 = load v788v1, !130
+        v97v1 = const u64 0
+        v790v1 = get_elem_ptr v789v1, __ptr ptr, v97v1, !131
+        v791v1 = load v790v1, !132
+        v95v1 = const u64 1
+        v100v1 = const u64 8, !133
+        v792v1 = mul v95v1, v100v1, !134
+        v793v1 = add v791v1, v792v1, !135
+        v794v1 = get_local __ptr __ptr { ptr }, self_00, !137
+        v795v1 = load v794v1, !138
+        v104v1 = const u64 0
+        v796v1 = get_elem_ptr v795v1, __ptr ptr, v104v1, !139
+        store v793v1 to v796v1, !140
+        v798v1 = get_local __ptr u64, v, !142
+        v799v1 = load v798v1, !143
+        v207v1 = const u64 0
+        v803v1 = get_elem_ptr v768v1, __ptr u64, v207v1, !144
+        store v799v1 to v803v1, !145
+        v836v1 = get_local __ptr { u64 }, __tmp_block_arg
+        mem_copy_val v836v1, v768v1
+        v204v1 = const u64 0
+        v807v1 = get_elem_ptr v763v1, __ptr { u64 }, v204v1, !146
+        mem_copy_val v807v1, v836v1
+        v840v1 = get_local __ptr { { u64 } }, __tmp_block_arg0
+        mem_copy_val v840v1, v763v1
+        v846v1 = get_local __ptr { { u64 } }, __tmp_block_arg1
+        mem_copy_val v846v1, v840v1
+        br decode_script_data_0_decode_from_raw_ptr_1_block2(v846v1), !147
 
-        decode_script_data_0_decode_from_raw_ptr_1_block2(v802v1: __ptr { { u64 } }):
-        v810v1 = get_local __ptr { { u64 } }, __tmp_block_arg2
-        mem_copy_val v810v1, v802v1
-        v814v1 = get_local __ptr { { u64 } }, __tmp_block_arg3
-        mem_copy_val v814v1, v810v1
-        v139v1 = get_local __ptr { { u64 } }, args, !136
-        mem_copy_val v139v1, v814v1
-        v163v1 = get_local __ptr { { u64 } }, args, !137
-        v164v1 = const u64 0
-        v165v1 = get_elem_ptr v163v1, __ptr { u64 }, v164v1, !138
-        v820v1 = get_local __ptr { u64 }, __tmp_arg
-        mem_copy_val v820v1, v165v1
-        v822v1 = call main_15(v820v1)
-        v168v1 = get_local __ptr u64, _result, !139
-        store v822v1 to v168v1, !139
-        v187v1 = get_local __ptr u64, _result, !140
-        v188v3 = get_local __ptr __ptr u64, item_, !143
-        store v187v1 to v188v3, !143
-        v785v1 = get_local __ptr bool, IS_TRIVIAL, !145
-        v173v1 = const bool true, !146
-        store v173v1 to v785v1, !147
-        v787v1 = get_local __ptr u64, size, !149
-        v178v1 = const u64 8
-        store v178v1 to v787v1, !150
-        v789v1 = get_local __ptr __ptr u64, item_, !152
-        v790v1 = load v789v1, !143
-        v791v1 = get_local __ptr u64, size, !154
-        v792v1 = load v791v1, !143
-        retd v790v1 v792v1, !156
+        decode_script_data_0_decode_from_raw_ptr_1_block2(v842v1: __ptr { { u64 } }):
+        v850v1 = get_local __ptr { { u64 } }, __tmp_block_arg2
+        mem_copy_val v850v1, v842v1
+        v854v1 = get_local __ptr { { u64 } }, __tmp_block_arg3
+        mem_copy_val v854v1, v850v1
+        v147v1 = get_local __ptr { { u64 } }, args, !148
+        mem_copy_val v147v1, v854v1
+        v171v1 = get_local __ptr { { u64 } }, args, !149
+        v172v1 = const u64 0
+        v173v1 = get_elem_ptr v171v1, __ptr { u64 }, v172v1, !150
+        v860v1 = get_local __ptr { u64 }, __tmp_arg
+        mem_copy_val v860v1, v173v1
+        v862v1 = call main_15(v860v1)
+        v176v1 = get_local __ptr u64, _result, !151
+        store v862v1 to v176v1, !151
+        v195v1 = get_local __ptr u64, _result, !152
+        v196v3 = get_local __ptr __ptr u64, item_, !155
+        store v195v1 to v196v3, !155
+        v825v1 = get_local __ptr bool, IS_TRIVIAL, !157
+        v181v1 = const bool true, !158
+        store v181v1 to v825v1, !159
+        v827v1 = get_local __ptr u64, size, !161
+        v186v1 = const u64 8
+        store v186v1 to v827v1, !162
+        v829v1 = get_local __ptr __ptr u64, item_, !164
+        v830v1 = load v829v1, !155
+        v831v1 = get_local __ptr u64, size, !166
+        v832v1 = load v831v1, !155
+        retd v830v1 v832v1, !168
     }
 
-    entry_orig fn main_15(baba: __ptr { u64 }) -> u64, !160 {
+    entry_orig fn main_15(baba: __ptr { u64 }) -> u64, !172 {
         local u64 other_
 
         entry(baba: __ptr { u64 }):
-        v157v1 = const u64 0
-        v158v1 = get_elem_ptr baba, __ptr u64, v157v1, !161
-        v649v1 = get_local __ptr u64, other_, !164
-        v160v1 = const u64 1, !165
-        store v160v1 to v649v1, !164
-        v652v1 = load v158v1, !164
-        v653v1 = get_local __ptr u64, other_, !167
-        v654v1 = load v653v1, !164
-        v655v1 = add v652v1, v654v1, !164
-        ret u64 v655v1
+        v165v1 = const u64 0
+        v166v1 = get_elem_ptr baba, __ptr u64, v165v1, !173
+        v681v1 = get_local __ptr u64, other_, !176
+        v168v1 = const u64 1, !177
+        store v168v1 to v681v1, !176
+        v684v1 = load v166v1, !176
+        v685v1 = get_local __ptr u64, other_, !179
+        v686v1 = load v685v1, !176
+        v687v1 = add v684v1, v686v1, !176
+        ret u64 v687v1
     }
 }
 
@@ -220,21 +230,21 @@ script {
 !5 = span !4 1542 1543
 !6 = span !0 66 103
 !7 = fn_call_path_span !0 66 84
-!8 = span !4 91615 91647
-!9 = fn_call_path_span !4 91615 91645
+!8 = span !4 105941 105973
+!9 = fn_call_path_span !4 105941 105971
 !10 = span !4 1525 1549
 !11 = (!6 !7 !8 !9 !10)
 !12 = (!6 !7 !8 !9 !10)
-!13 = span !4 91590 91648
-!14 = fn_call_path_span !4 91590 91609
+!13 = span !4 105916 105974
+!14 = fn_call_path_span !4 105916 105935
 !15 = (!6 !7 !13 !14)
 !16 = (!6 !7 !13 !14)
-!17 = span !4 91330 91354
-!18 = fn_call_path_span !4 91330 91347
+!17 = span !4 105656 105680
+!18 = fn_call_path_span !4 105656 105673
 !19 = span !4 3731 3753
 !20 = fn_call_path_span !4 3731 3751
-!21 = span !4 54488 54545
-!22 = fn_call_path_span !4 54515 54517
+!21 = span !4 61659 61716
+!22 = fn_call_path_span !4 61686 61688
 !23 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22)
 !24 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22)
 !25 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22)
@@ -247,138 +257,150 @@ script {
 !32 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22 !31)
 !33 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22)
 !34 = (!6 !7 !13 !14 !17 !18 !19 !20 !21 !22)
-!35 = span !4 54488 54573
+!35 = span !4 61651 61717
 !36 = (!6 !7 !13 !14 !17 !18 !19 !20 !35)
-!37 = span !4 54549 54573
-!38 = fn_call_path_span !4 54549 54566
-!39 = span !0 157 214
-!40 = fn_call_path_span !0 184 186
-!41 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!42 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!43 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!44 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!45 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40 !28)
-!46 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!47 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40 !31)
-!48 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!49 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !39 !40)
-!50 = span !0 157 244
-!51 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !50)
-!52 = span !4 51022 51026
-!53 = (!6 !7 !13 !14 !17 !18 !19 !20 !37 !38 !19 !20 !50)
-!54 = (!6 !7 !13 !14 !17 !18 !19 !20 !35)
-!55 = (!6 !7 !13 !14 !17)
-!56 = span !4 91406 91409
-!57 = (!6 !7 !13 !14 !56)
-!58 = (!6 !7 !13 !14)
-!59 = (!6 !7 !13 !14)
-!60 = span !4 91365 91411
-!61 = (!6 !7 !13 !14 !60)
-!62 = (!6 !7 !13 !14 !60)
-!63 = span !4 91421 91424
-!64 = (!6 !7 !13 !14 !63)
-!65 = (!6 !7 !13 !14)
-!66 = (!6 !7 !13 !14)
-!67 = span !4 91463 91483
-!68 = (!6 !7 !13 !14 !67)
-!69 = span !4 91478 91481
-!70 = (!6 !7 !13 !14 !69)
-!71 = (!6 !7 !13 !14 !67)
-!72 = span !4 91446 91484
+!37 = (!6 !7 !13 !14 !17 !18 !19 !20 !35)
+!38 = span !4 61734 61735
+!39 = (!6 !7 !13 !14 !17 !18 !19 !20 !38)
+!40 = (!6 !7 !13 !14 !17 !18 !19 !20)
+!41 = span !4 61734 61763
+!42 = (!6 !7 !13 !14 !17 !18 !19 !20 !41)
+!43 = span !4 61739 61763
+!44 = fn_call_path_span !4 61739 61756
+!45 = span !0 157 214
+!46 = fn_call_path_span !0 184 186
+!47 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!48 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!49 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!50 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!51 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46 !28)
+!52 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!53 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46 !31)
+!54 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!55 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !45 !46)
+!56 = span !0 157 244
+!57 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !56)
+!58 = span !4 58185 58189
+!59 = (!6 !7 !13 !14 !17 !18 !19 !20 !43 !44 !19 !20 !56)
+!60 = (!6 !7 !13 !14 !17 !18 !19 !20 !41)
+!61 = span !4 61726 61764
+!62 = (!6 !7 !13 !14 !17 !18 !19 !20 !61)
+!63 = (!6 !7 !13 !14 !17 !18 !19 !20 !61)
+!64 = span !4 61773 61774
+!65 = (!6 !7 !13 !14 !17 !18 !19 !20 !64)
+!66 = (!6 !7 !13 !14 !17 !18 !19 !20)
+!67 = (!6 !7 !13 !14 !17)
+!68 = span !4 105732 105735
+!69 = (!6 !7 !13 !14 !68)
+!70 = (!6 !7 !13 !14)
+!71 = (!6 !7 !13 !14)
+!72 = span !4 105691 105737
 !73 = (!6 !7 !13 !14 !72)
-!74 = span !4 91507 91513
-!75 = (!6 !7 !13 !14 !74)
-!76 = span !4 91493 91514
-!77 = fn_call_path_span !4 91493 91506
-!78 = (!6 !7 !13 !14 !76 !77)
-!79 = (!6 !7 !13 !14 !76 !77)
-!80 = span !4 54646 54671
-!81 = (!6 !7 !13 !14 !76 !77 !80)
-!82 = span !4 54661 54667
-!83 = (!6 !7 !13 !14 !76 !77 !82)
-!84 = span !4 54647 54668
-!85 = fn_call_path_span !4 54647 54660
-!86 = (!6 !7 !13 !14 !76 !77 !84 !85)
-!87 = span !0 373 410
-!88 = (!6 !7 !13 !14 !76 !77 !84 !85 !87)
-!89 = span !0 385 391
-!90 = (!6 !7 !13 !14 !76 !77 !84 !85 !89)
-!91 = span !0 385 407
-!92 = fn_call_path_span !0 392 398
-!93 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92)
-!94 = span !4 3480 3484
-!95 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !94)
-!96 = span !4 3466 3485
-!97 = fn_call_path_span !4 3466 3479
-!98 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97)
-!99 = span !4 51098 51104
-!100 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !99)
-!101 = span !4 51098 51126
-!102 = fn_call_path_span !4 51105 51117
-!103 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!104 = span !4 2282 2286
-!105 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !104)
-!106 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!107 = span !4 625 641
-!108 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !107)
-!109 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!110 = span !4 2273 2354
-!111 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !110)
-!112 = span !4 2311 2324
-!113 = span !4 2265 2355
-!114 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !113)
-!115 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !113)
-!116 = span !4 2391 2395
-!117 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !116)
-!118 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!119 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !107)
-!120 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!121 = span !4 2401 2402
-!122 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!123 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!124 = span !4 2364 2403
-!125 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !124)
-!126 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!127 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !124)
-!128 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !124)
-!129 = span !4 2413 2414
-!130 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102 !129)
-!131 = (!6 !7 !13 !14 !76 !77 !84 !85 !91 !92 !96 !97 !101 !102)
-!132 = (!6 !7 !13 !14 !76 !77 !84 !85 !87)
-!133 = (!6 !7 !13 !14 !76 !77 !84 !85 !87)
-!134 = (!6 !7 !13 !14 !76 !77 !80)
-!135 = (!6 !7 !13 !14)
-!136 = span !0 40 104
-!137 = span !0 145 149
-!138 = span !0 150 151
-!139 = span !0 121 153
-!140 = span !0 196 203
-!141 = span !0 170 204
-!142 = fn_call_path_span !0 170 187
-!143 = (!141 !142)
-!144 = span !4 49045 49094
-!145 = (!141 !142 !144)
-!146 = span !4 49070 49094
-!147 = (!141 !142 !144)
-!148 = span !4 49124 49152
-!149 = (!141 !142 !148)
-!150 = (!141 !142 !148)
-!151 = span !4 49176 49180
-!152 = (!141 !142 !151)
-!153 = span !4 49182 49186
-!154 = (!141 !142 !153)
-!155 = span !4 49161 49187
-!156 = (!141 !142 !155)
-!157 = "test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_ref/src/main.sw"
-!158 = span !157 46 99
-!159 = fn_name_span !157 49 53
-!160 = (!158 !159)
-!161 = span !157 33 41
-!162 = span !157 85 97
-!163 = fn_call_path_span !157 94 95
-!164 = (!162 !163)
-!165 = span !157 96 97
-!166 = span !27 1328 1333
-!167 = (!162 !163 !166)
+!74 = (!6 !7 !13 !14 !72)
+!75 = span !4 105747 105750
+!76 = (!6 !7 !13 !14 !75)
+!77 = (!6 !7 !13 !14)
+!78 = (!6 !7 !13 !14)
+!79 = span !4 105789 105809
+!80 = (!6 !7 !13 !14 !79)
+!81 = span !4 105804 105807
+!82 = (!6 !7 !13 !14 !81)
+!83 = (!6 !7 !13 !14 !79)
+!84 = span !4 105772 105810
+!85 = (!6 !7 !13 !14 !84)
+!86 = span !4 105833 105839
+!87 = (!6 !7 !13 !14 !86)
+!88 = span !4 105819 105840
+!89 = fn_call_path_span !4 105819 105832
+!90 = (!6 !7 !13 !14 !88 !89)
+!91 = (!6 !7 !13 !14 !88 !89)
+!92 = span !4 61847 61872
+!93 = (!6 !7 !13 !14 !88 !89 !92)
+!94 = span !4 61862 61868
+!95 = (!6 !7 !13 !14 !88 !89 !94)
+!96 = span !4 61848 61869
+!97 = fn_call_path_span !4 61848 61861
+!98 = (!6 !7 !13 !14 !88 !89 !96 !97)
+!99 = span !0 373 410
+!100 = (!6 !7 !13 !14 !88 !89 !96 !97 !99)
+!101 = span !0 385 391
+!102 = (!6 !7 !13 !14 !88 !89 !96 !97 !101)
+!103 = span !0 385 407
+!104 = fn_call_path_span !0 392 398
+!105 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104)
+!106 = span !4 3480 3484
+!107 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !106)
+!108 = span !4 3466 3485
+!109 = fn_call_path_span !4 3466 3479
+!110 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109)
+!111 = span !4 58261 58267
+!112 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !111)
+!113 = span !4 58261 58289
+!114 = fn_call_path_span !4 58268 58280
+!115 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!116 = span !4 2282 2286
+!117 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !116)
+!118 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!119 = span !4 625 641
+!120 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !119)
+!121 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!122 = span !4 2273 2354
+!123 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !122)
+!124 = span !4 2311 2324
+!125 = span !4 2265 2355
+!126 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !125)
+!127 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !125)
+!128 = span !4 2391 2395
+!129 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !128)
+!130 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!131 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !119)
+!132 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!133 = span !4 2401 2402
+!134 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!135 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!136 = span !4 2364 2403
+!137 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !136)
+!138 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!139 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !136)
+!140 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !136)
+!141 = span !4 2413 2414
+!142 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114 !141)
+!143 = (!6 !7 !13 !14 !88 !89 !96 !97 !103 !104 !108 !109 !113 !114)
+!144 = (!6 !7 !13 !14 !88 !89 !96 !97 !99)
+!145 = (!6 !7 !13 !14 !88 !89 !96 !97 !99)
+!146 = (!6 !7 !13 !14 !88 !89 !92)
+!147 = (!6 !7 !13 !14)
+!148 = span !0 40 104
+!149 = span !0 145 149
+!150 = span !0 150 151
+!151 = span !0 121 153
+!152 = span !0 196 203
+!153 = span !0 170 204
+!154 = fn_call_path_span !0 170 187
+!155 = (!153 !154)
+!156 = span !4 56208 56257
+!157 = (!153 !154 !156)
+!158 = span !4 56233 56257
+!159 = (!153 !154 !156)
+!160 = span !4 56287 56315
+!161 = (!153 !154 !160)
+!162 = (!153 !154 !160)
+!163 = span !4 56339 56343
+!164 = (!153 !154 !163)
+!165 = span !4 56345 56349
+!166 = (!153 !154 !165)
+!167 = span !4 56324 56350
+!168 = (!153 !154 !167)
+!169 = "test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_ref/src/main.sw"
+!170 = span !169 46 99
+!171 = fn_name_span !169 49 53
+!172 = (!170 !171)
+!173 = span !169 33 41
+!174 = span !169 85 97
+!175 = fn_call_path_span !169 94 95
+!176 = (!174 !175)
+!177 = span !169 96 97
+!178 = span !27 1328 1333
+!179 = (!174 !175 !178)
 
-    Finished debug [unoptimized + fuel] target(s) [448 B] in ???
+    Finished debug [unoptimized + fuel] target(s) [480 B] in ???
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_two_u64/stdout.snap
```diff
@@ -34,80 +34,80 @@ script {
         local mut { ptr } buffer
 
         entry():
-        v111v1 = const u64 0, !5
-        v355v1 = gtf v111v1, 10, !11
-        v356v1 = bitcast v355v1 to ptr, !12
-        v28v1 = const bool true, !13
-        cbr v28v1, decode_script_data_0_decode_from_raw_ptr_1_block0(), decode_script_data_0_decode_from_raw_ptr_1_block1(), !17
+        v123v1 = const u64 0, !5
+        v385v1 = gtf v123v1, 10, !11
+        v386v1 = bitcast v385v1 to ptr, !12
+        v32v1 = const bool true, !13
+        cbr v32v1, decode_script_data_0_decode_from_raw_ptr_1_block0(), decode_script_data_0_decode_from_raw_ptr_1_block1(), !17
 
         decode_script_data_0_decode_from_raw_ptr_1_block0():
-        v399v1 = cast_ptr v356v1 to __ptr { u64, u64 }, !18
-        v439v1 = get_local __ptr { u64, u64 }, __aggr_memcpy_0
-        mem_copy_val v439v1, v399v1
-        v436v1 = get_local __ptr { u64, u64 }, __tmp_block_arg
-        mem_copy_val v436v1, v439v1
-        br decode_script_data_0_decode_from_raw_ptr_1_block2(v436v1), !19
+        v435v1 = cast_ptr v386v1 to __ptr { u64, u64 }, !18
+        v475v1 = get_local __ptr { u64, u64 }, __aggr_memcpy_0
+        mem_copy_val v475v1, v435v1
+        v472v1 = get_local __ptr { u64, u64 }, __tmp_block_arg
+        mem_copy_val v472v1, v475v1
+        br decode_script_data_0_decode_from_raw_ptr_1_block2(v472v1), !19
 
         decode_script_data_0_decode_from_raw_ptr_1_block1():
-        v376v1 = get_local __ptr { ptr }, __struct_init_0, !21
-        v179v1 = const u64 0
-        v378v1 = get_elem_ptr v376v1, __ptr ptr, v179v1, !22
-        store v356v1 to v378v1, !23
-        v381v1 = get_local __ptr { ptr }, buffer, !25
-        mem_copy_val v381v1, v376v1
-        v383v1 = get_local __ptr { ptr }, buffer, !27
-        v386v1 = get_local __ptr { u64, u64 }, __tuple_init_0, !31
-        v68v1 = const u64 0
-        v388v3 = get_elem_ptr v383v1, __ptr ptr, v68v1, !37
-        v413v1 = load v388v3, !38
-        v414v1 = asm(ptr: v413v1, val) -> u64 val, !40 {
+        v412v1 = get_local __ptr { ptr }, __struct_init_0, !21
+        v191v1 = const u64 0
+        v414v1 = get_elem_ptr v412v1, __ptr ptr, v191v1, !22
+        store v386v1 to v414v1, !23
+        v417v1 = get_local __ptr { ptr }, buffer, !25
+        mem_copy_val v417v1, v412v1
+        v419v1 = get_local __ptr { ptr }, buffer, !27
+        v422v1 = get_local __ptr { u64, u64 }, __tuple_init_0, !31
+        v80v1 = const u64 0
+        v424v3 = get_elem_ptr v419v1, __ptr ptr, v80v1, !37
+        v449v1 = load v424v3, !38
+        v450v1 = asm(ptr: v449v1, val) -> u64 val, !40 {
             lw     val ptr i0, !41
         }
-        v416v1 = load v388v3, !42
-        v417v1 = const u64 8, !43
-        v418v1 = add v416v1, v417v1, !44
-        store v418v1 to v388v3, !46
-        v423v1 = load v388v3, !49
-        v424v1 = asm(ptr: v423v1, val) -> u64 val, !50 {
+        v452v1 = load v424v3, !42
+        v453v1 = const u64 8, !43
+        v454v1 = add v452v1, v453v1, !44
+        store v454v1 to v424v3, !46
+        v459v1 = load v424v3, !49
+        v460v1 = asm(ptr: v459v1, val) -> u64 val, !50 {
             lw     val ptr i0, !41
         }
-        v426v1 = load v388v3, !51
-        v427v1 = const u64 8, !52
-        v428v1 = add v426v1, v427v1, !53
-        store v428v1 to v388v3, !54
-        v182v1 = const u64 0
-        v391v1 = get_elem_ptr v386v1, __ptr u64, v182v1, !55
-        store v414v1 to v391v1, !56
-        v185v1 = const u64 1
-        v393v1 = get_elem_ptr v386v1, __ptr u64, v185v1, !57
-        store v424v1 to v393v1, !58
-        v434v1 = get_local __ptr { u64, u64 }, __tmp_block_arg
-        mem_copy_val v434v1, v386v1
-        br decode_script_data_0_decode_from_raw_ptr_1_block2(v434v1), !59
+        v462v1 = load v424v3, !51
+        v463v1 = const u64 8, !52
+        v464v1 = add v462v1, v463v1, !53
+        store v464v1 to v424v3, !54
+        v194v1 = const u64 0
+        v427v1 = get_elem_ptr v422v1, __ptr u64, v194v1, !55
+        store v450v1 to v427v1, !56
+        v197v1 = const u64 1
+        v429v1 = get_elem_ptr v422v1, __ptr u64, v197v1, !57
+        store v460v1 to v429v1, !58
+        v470v1 = get_local __ptr { u64, u64 }, __tmp_block_arg
+        mem_copy_val v470v1, v422v1
+        br decode_script_data_0_decode_from_raw_ptr_1_block2(v470v1), !59
 
-        decode_script_data_0_decode_from_raw_ptr_1_block2(v432v1: __ptr { u64, u64 }):
-        v119v1 = get_local __ptr { u64, u64 }, args, !60
-        mem_copy_val v119v1, v432v1
-        v145v1 = get_local __ptr { u64, u64 }, args, !61
-        v146v1 = const u64 0
-        v147v1 = get_elem_ptr v145v1, __ptr u64, v146v1, !62
-        v148v1 = load v147v1
-        v149v1 = get_local __ptr { u64, u64 }, args, !63
-        v150v1 = const u64 1
-        v151v1 = get_elem_ptr v149v1, __ptr u64, v150v1, !64
-        v152v1 = load v151v1
-        v153v1 = call main_11(v148v1, v152v1), !67
-        v154v1 = get_local __ptr u64, _result, !68
-        store v153v1 to v154v1, !68
-        v173v1 = get_local __ptr u64, _result, !69
-        v164v1 = const u64 8
-        retd v173v1 v164v1, !73
+        decode_script_data_0_decode_from_raw_ptr_1_block2(v468v1: __ptr { u64, u64 }):
+        v131v1 = get_local __ptr { u64, u64 }, args, !60
+        mem_copy_val v131v1, v468v1
+        v157v1 = get_local __ptr { u64, u64 }, args, !61
+        v158v1 = const u64 0
+        v159v1 = get_elem_ptr v157v1, __ptr u64, v158v1, !62
+        v160v1 = load v159v1
+        v161v1 = get_local __ptr { u64, u64 }, args, !63
+        v162v1 = const u64 1
+        v163v1 = get_elem_ptr v161v1, __ptr u64, v162v1, !64
+        v164v1 = load v163v1
+        v165v1 = call main_11(v160v1, v164v1), !67
+        v166v1 = get_local __ptr u64, _result, !68
+        store v165v1 to v166v1, !68
+        v185v1 = get_local __ptr u64, _result, !69
+        v176v1 = const u64 8
+        retd v185v1 v176v1, !73
     }
 
     entry_orig fn main_11(baba !75: u64, keke !76: u64) -> u64, !79 {
         entry(baba: u64, keke: u64):
-        v340v1 = add baba, keke, !82
-        ret u64 v340v1
+        v370v1 = add baba, keke, !82
+        ret u64 v370v1
     }
 }
 
@@ -119,34 +119,34 @@ script {
 !5 = span !4 1542 1543
 !6 = span !0 64 99
 !7 = fn_call_path_span !0 64 82
-!8 = span !4 91615 91647
-!9 = fn_call_path_span !4 91615 91645
+!8 = span !4 105941 105973
+!9 = fn_call_path_span !4 105941 105971
 !10 = span !4 1525 1549
 !11 = (!6 !7 !8 !9 !10)
 !12 = (!6 !7 !8 !9 !10)
-!13 = span !4 51022 51026
-!14 = span !4 91590 91648
-!15 = fn_call_path_span !4 91590 91609
-!16 = span !4 91330 91354
+!13 = span !4 58185 58189
+!14 = span !4 105916 105974
+!15 = fn_call_path_span !4 105916 105935
+!16 = span !4 105656 105680
 !17 = (!6 !7 !14 !15 !16)
 !18 = (!6 !7 !14 !15)
 !19 = (!6 !7 !14 !15)
-!20 = span !4 91463 91483
+!20 = span !4 105789 105809
 !21 = (!6 !7 !14 !15 !20)
 !22 = (!6 !7 !14 !15 !20)
 !23 = (!6 !7 !14 !15 !20)
-!24 = span !4 91446 91484
+!24 = span !4 105772 105810
 !25 = (!6 !7 !14 !15 !24)
-!26 = span !4 91507 91513
+!26 = span !4 105833 105839
 !27 = (!6 !7 !14 !15 !26)
-!28 = span !4 91493 91514
-!29 = fn_call_path_span !4 91493 91506
-!30 = span !4 54987 55033
+!28 = span !4 105819 105840
+!29 = fn_call_path_span !4 105819 105832
+!30 = span !4 62245 62291
 !31 = (!6 !7 !14 !15 !28 !29 !30)
-!32 = span !4 54988 55009
-!33 = fn_call_path_span !4 54988 55001
-!34 = span !4 51098 51126
-!35 = fn_call_path_span !4 51105 51117
+!32 = span !4 62246 62267
+!33 = fn_call_path_span !4 62246 62259
+!34 = span !4 58261 58289
+!35 = fn_call_path_span !4 58268 58280
 !36 = span !4 625 641
 !37 = (!6 !7 !14 !15 !28 !29 !32 !33 !34 !35 !36)
 !38 = (!6 !7 !14 !15 !28 !29 !32 !33 !34 !35)
@@ -158,8 +158,8 @@ script {
 !44 = (!6 !7 !14 !15 !28 !29 !32 !33 !34 !35)
 !45 = span !4 2364 2403
 !46 = (!6 !7 !14 !15 !28 !29 !32 !33 !34 !35 !45)
-!47 = span !4 55011 55032
-!48 = fn_call_path_span !4 55011 55024
+!47 = span !4 62269 62290
+!48 = fn_call_path_span !4 62269 62282
 !49 = (!6 !7 !14 !15 !28 !29 !47 !48 !34 !35)
 !50 = (!6 !7 !14 !15 !28 !29 !47 !48 !34 !35 !39)
 !51 = (!6 !7 !14 !15 !28 !29 !47 !48 !34 !35)
@@ -183,7 +183,7 @@ script {
 !69 = span !0 200 207
 !70 = span !0 174 208
 !71 = fn_call_path_span !0 174 191
-!72 = span !4 49161 49187
+!72 = span !4 56324 56350
 !73 = (!70 !71 !72)
 !74 = "test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_two_u64/src/main.sw"
 !75 = span !74 17 21
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/main_args/main_args_various_types/stdout.snap
```diff
@@ -54,182 +54,182 @@ script {
         local slice slice_
 
         entry():
-        v472v1 = const u64 0, !5
-        v4042v1 = gtf v472v1, 10, !11
-        v4043v1 = bitcast v4042v1 to ptr, !12
-        v4085v1 = get_local __ptr { ptr }, __struct_init_0, !16
-        v1130v1 = const u64 0
-        v4087v1 = get_elem_ptr v4085v1, __ptr ptr, v1130v1, !17
-        store v4043v1 to v4087v1, !18
-        v4090v1 = get_local __ptr { ptr }, buffer, !20
-        mem_copy_val v4090v1, v4085v1
-        v4092v1 = get_local __ptr { ptr }, buffer, !22
-        v4095v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, __tuple_init_0, !26
-        v4099v1 = get_local __ptr [u8; 48], __array_init_0, !30
-        mem_clear_val v4099v1, !31
-        v4102v1 = get_local __ptr [u8; 48], array, !33
-        mem_copy_val v4102v1, v4099v1
-        v4104v1 = get_local __ptr [u8; 48], array, !35
-        v4105v1 = cast_ptr v4104v1 to __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], !36
-        v194v1 = const u64 0, !37
-        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v194v1), !38
+        v492v1 = const u64 0, !5
+        v4158v1 = gtf v492v1, 10, !11
+        v4159v1 = bitcast v4158v1 to ptr, !12
+        v4211v1 = get_local __ptr { ptr }, __struct_init_0, !16
+        v1162v1 = const u64 0
+        v4213v1 = get_elem_ptr v4211v1, __ptr ptr, v1162v1, !17
+        store v4159v1 to v4213v1, !18
+        v4216v1 = get_local __ptr { ptr }, buffer, !20
+        mem_copy_val v4216v1, v4211v1
+        v4218v1 = get_local __ptr { ptr }, buffer, !22
+        v4221v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, __tuple_init_0, !26
+        v4225v1 = get_local __ptr [u8; 48], __array_init_0, !30
+        mem_clear_val v4225v1, !31
+        v4228v1 = get_local __ptr [u8; 48], array, !33
+        mem_copy_val v4228v1, v4225v1
+        v4230v1 = get_local __ptr [u8; 48], array, !35
+        v4231v1 = cast_ptr v4230v1 to __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], !36
+        v214v1 = const u64 0, !37
+        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v214v1), !38
 
-        decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v4022v1: u64):
-        v212v1 = const u64 2
-        v4114v1 = cmp lt v4022v1 v212v1, !41
-        cbr v4114v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while_body(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_end_while(), !42
+        decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v4138v1: u64):
+        v232v1 = const u64 2
+        v4240v1 = cmp lt v4138v1 v232v1, !41
+        cbr v4240v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while_body(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_end_while(), !42
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while_body():
-        v218v1 = const u64 24
-        v4127v1 = asm(idx: v4022v1, elem_ir_type_size: v218v1, ptr: v4105v1, offset_temp, ptr_out) -> __ptr { { string<3> }, { u64, ( u64 | u64 ) } } ptr_out, !43 {
+        v238v1 = const u64 24
+        v4253v1 = asm(idx: v4138v1, elem_ir_type_size: v238v1, ptr: v4231v1, offset_temp, ptr_out) -> __ptr { { string<3> }, { u64, ( u64 | u64 ) } } ptr_out, !43 {
             mul    offset_temp idx elem_ir_type_size
             add    ptr_out ptr offset_temp
         }
-        v4133v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, __tuple_init_00, !49
-        v4136v1 = get_local __ptr { string<3> }, __struct_init_00, !53
-        v4144v1 = get_local __ptr { ptr, u64 }, __tuple_init_000, !59
-        v247v1 = const u64 0
-        v4146v1 = get_elem_ptr v4092v1, __ptr ptr, v247v1, !61
-        v1145v1 = const u64 0
-        v4149v1 = get_elem_ptr v4144v1, __ptr ptr, v1145v1, !62
-        mem_copy_val v4149v1, v4146v1
-        v1148v1 = const u64 1
-        v4151v1 = get_elem_ptr v4144v1, __ptr u64, v1148v1, !63
-        v276v1 = const u64 3
-        store v276v1 to v4151v1, !64
-        v4392v1 = asm(ptr: v4144v1) -> __ptr slice ptr {
+        v4259v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, __tuple_init_00, !49
+        v4262v1 = get_local __ptr { string<3> }, __struct_init_00, !53
+        v4270v1 = get_local __ptr { ptr, u64 }, __tuple_init_000, !59
+        v267v1 = const u64 0
+        v4272v1 = get_elem_ptr v4218v1, __ptr ptr, v267v1, !61
+        v1177v1 = const u64 0
+        v4275v1 = get_elem_ptr v4270v1, __ptr ptr, v1177v1, !62
+        mem_copy_val v4275v1, v4272v1
+        v1180v1 = const u64 1
+        v4277v1 = get_elem_ptr v4270v1, __ptr u64, v1180v1, !63
+        v296v1 = const u64 3
+        store v296v1 to v4277v1, !64
+        v4518v1 = asm(ptr: v4270v1) -> __ptr slice ptr {
         }
-        v4420v1 = get_local __ptr slice, __aggr_memcpy_0
-        mem_copy_val v4420v1, v4392v1
-        v4155v1 = get_local __ptr slice, slice, !66
-        mem_copy_val v4155v1, v4420v1
-        v4159v1 = load v4146v1, !67
-        v4161v1 = const u64 3, !68
-        v4162v1 = add v4159v1, v4161v1, !69
-        store v4162v1 to v4146v1, !71
-        v4166v1 = get_local __ptr slice, slice, !73
-        v4169v1 = get_local __ptr slice, data, !75
-        mem_copy_val v4169v1, v4166v1
-        v4171v1 = get_local __ptr slice, data, !77
-        v4173v1 = get_local __ptr slice, self_00000, !80
-        mem_copy_val v4173v1, v4171v1
-        v4175v1 = get_local __ptr slice, self_00000, !83
-        v4177v1 = get_local __ptr slice, slice_, !86
-        mem_copy_val v4177v1, v4175v1
-        v4179v1 = get_local __ptr slice, slice_, !88
-        v4394v1 = asm(ptr: v4179v1) -> __ptr { ptr, u64 } ptr {
+        v4546v1 = get_local __ptr slice, __aggr_memcpy_0
+        mem_copy_val v4546v1, v4518v1
+        v4281v1 = get_local __ptr slice, slice, !66
+        mem_copy_val v4281v1, v4546v1
+        v4285v1 = load v4272v1, !67
+        v4287v1 = const u64 3, !68
+        v4288v1 = add v4285v1, v4287v1, !69
+        store v4288v1 to v4272v1, !71
+        v4292v1 = get_local __ptr slice, slice, !73
+        v4295v1 = get_local __ptr slice, data, !75
+        mem_copy_val v4295v1, v4292v1
+        v4297v1 = get_local __ptr slice, data, !77
+        v4299v1 = get_local __ptr slice, self_00000, !80
+        mem_copy_val v4299v1, v4297v1
+        v4301v1 = get_local __ptr slice, self_00000, !83
+        v4303v1 = get_local __ptr slice, slice_, !86
+        mem_copy_val v4303v1, v4301v1
+        v4305v1 = get_local __ptr slice, slice_, !88
+        v4520v1 = asm(ptr: v4305v1) -> __ptr { ptr, u64 } ptr {
         }
-        v4426v1 = get_local __ptr { ptr, u64 }, __aggr_memcpy_00
-        mem_copy_val v4426v1, v4394v1
-        v4183v1 = get_local __ptr { ptr, u64 }, __anon_0, !89
-        mem_copy_val v4183v1, v4426v1
-        v295v1 = const u64 0
-        v4185v1 = get_elem_ptr v4183v1, __ptr ptr, v295v1, !91
-        v4186v1 = load v4185v1, !92
-        v4396v1 = asm(s: v4186v1) -> __ptr string<3> s {
+        v4552v1 = get_local __ptr { ptr, u64 }, __aggr_memcpy_00
+        mem_copy_val v4552v1, v4520v1
+        v4309v1 = get_local __ptr { ptr, u64 }, __anon_0, !89
+        mem_copy_val v4309v1, v4552v1
+        v315v1 = const u64 0
+        v4311v1 = get_elem_ptr v4309v1, __ptr ptr, v315v1, !91
+        v4312v1 = load v4311v1, !92
+        v4522v1 = asm(s: v4312v1) -> __ptr string<3> s {
         }
-        v4429v1 = get_local __ptr string<3>, __aggr_memcpy_01
-        mem_copy_val v4429v1, v4396v1
-        v1142v1 = const u64 0
-        v4191v1 = get_elem_ptr v4136v1, __ptr string<3>, v1142v1, !93
-        mem_copy_val v4191v1, v4429v1
-        v4288v1 = load v4146v1, !100
-        v4289v1 = asm(ptr: v4288v1, val) -> u64 val, !102 {
+        v4555v1 = get_local __ptr string<3>, __aggr_memcpy_01
+        mem_copy_val v4555v1, v4522v1
+        v1174v1 = const u64 0
+        v4317v1 = get_elem_ptr v4262v1, __ptr string<3>, v1174v1, !93
+        mem_copy_val v4317v1, v4555v1
+        v4414v1 = load v4272v1, !100
+        v4415v1 = asm(ptr: v4414v1, val) -> u64 val, !102 {
             lw     val ptr i0, !103
         }
-        v4291v1 = load v4146v1, !104
-        v4292v1 = const u64 8, !105
-        v4293v1 = add v4291v1, v4292v1, !106
-        store v4293v1 to v4146v1, !108
-        v371v1 = const u64 0, !109
-        v4207v1 = cmp eq v4289v1 v371v1, !112
-        cbr v4207v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block0(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block1(), !113
+        v4417v1 = load v4272v1, !104
+        v4418v1 = const u64 8, !105
+        v4419v1 = add v4417v1, v4418v1, !106
+        store v4419v1 to v4272v1, !108
+        v391v1 = const u64 0, !109
+        v4333v1 = cmp eq v4415v1 v391v1, !112
+        cbr v4333v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block0(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block1(), !113
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block0():
-        v4229v1 = get_local __ptr { u64, ( u64 | u64 ) }, __anon_00, !116
-        v375v1 = const u64 0
-        v4230v1 = get_elem_ptr v4229v1, __ptr u64, v375v1, !117
-        v373v1 = const u64 0, !115
-        store v373v1 to v4230v1, !118
-        v4298v1 = load v4146v1, !121
-        v4299v1 = asm(ptr: v4298v1, val) -> u64 val, !122 {
+        v4355v1 = get_local __ptr { u64, ( u64 | u64 ) }, __anon_00, !116
+        v395v1 = const u64 0
+        v4356v1 = get_elem_ptr v4355v1, __ptr u64, v395v1, !117
+        v393v1 = const u64 0, !115
+        store v393v1 to v4356v1, !118
+        v4424v1 = load v4272v1, !121
+        v4425v1 = asm(ptr: v4424v1, val) -> u64 val, !122 {
             lw     val ptr i0, !103
         }
-        v4301v1 = load v4146v1, !123
-        v4302v1 = const u64 8, !124
-        v4303v1 = add v4301v1, v4302v1, !125
-        store v4303v1 to v4146v1, !126
-        v381v1 = const u64 1
-        v382v1 = const u64 0
-        v4234v1 = get_elem_ptr v4229v1, __ptr u64, v381v1, v382v1, !127
-        store v4299v1 to v4234v1, !128
-        v4321v1 = get_local __ptr { u64, ( u64 | u64 ) }, __tmp_block_arg
-        mem_copy_val v4321v1, v4229v1
-        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4321v1), !129
+        v4427v1 = load v4272v1, !123
+        v4428v1 = const u64 8, !124
+        v4429v1 = add v4427v1, v4428v1, !125
+        store v4429v1 to v4272v1, !126
+        v401v1 = const u64 1
+        v402v1 = const u64 0
+        v4360v1 = get_elem_ptr v4355v1, __ptr u64, v401v1, v402v1, !127
+        store v4425v1 to v4360v1, !128
+        v4447v1 = get_local __ptr { u64, ( u64 | u64 ) }, __tmp_block_arg
+        mem_copy_val v4447v1, v4355v1
+        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4447v1), !129
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block1():
-        v388v1 = const u64 1, !130
-        v4215v1 = cmp eq v4289v1 v388v1, !133
-        cbr v4215v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block2(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block3(), !134
+        v408v1 = const u64 1, !130
+        v4341v1 = cmp eq v4415v1 v408v1, !133
+        cbr v4341v1, decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block2(), decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block3(), !134
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block2():
-        v4219v1 = get_local __ptr { u64, ( u64 | u64 ) }, __anon_1, !135
-        v392v1 = const u64 0
-        v4220v1 = get_elem_ptr v4219v1, __ptr u64, v392v1, !136
-        v390v1 = const u64 1, !115
-        store v390v1 to v4220v1, !137
-        v4308v1 = load v4146v1, !140
-        v4309v1 = asm(ptr: v4308v1, val) -> u64 val, !141 {
+        v4345v1 = get_local __ptr { u64, ( u64 | u64 ) }, __anon_1, !135
+        v412v1 = const u64 0
+        v4346v1 = get_elem_ptr v4345v1, __ptr u64, v412v1, !136
+        v410v1 = const u64 1, !115
+        store v410v1 to v4346v1, !137
+        v4434v1 = load v4272v1, !140
+        v4435v1 = asm(ptr: v4434v1, val) -> u64 val, !141 {
             lw     val ptr i0, !103
         }
-        v4311v1 = load v4146v1, !142
-        v4312v1 = const u64 8, !143
-        v4313v1 = add v4311v1, v4312v1, !144
-        store v4313v1 to v4146v1, !145
-        v398v1 = const u64 1
-        v399v1 = const u64 1
-        v4224v1 = get_elem_ptr v4219v1, __ptr u64, v398v1, v399v1, !146
-        store v4309v1 to v4224v1, !147
-        v4319v1 = get_local __ptr { u64, ( u64 | u64 ) }, __tmp_block_arg
-        mem_copy_val v4319v1, v4219v1
-        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4319v1), !148
+        v4437v1 = load v4272v1, !142
+        v4438v1 = const u64 8, !143
+        v4439v1 = add v4437v1, v4438v1, !144
+        store v4439v1 to v4272v1, !145
+        v418v1 = const u64 1
+        v419v1 = const u64 1
+        v4350v1 = get_elem_ptr v4345v1, __ptr u64, v418v1, v419v1, !146
+        store v4435v1 to v4350v1, !147
+        v4445v1 = get_local __ptr { u64, ( u64 | u64 ) }, __tmp_block_arg
+        mem_copy_val v4445v1, v4345v1
+        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4445v1), !148
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block3():
-        v403v1 = const u64 0, !149
-        revert v403v1, !151
+        v423v1 = const u64 0, !149
+        revert v423v1, !151
 
-        decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4317v1: __ptr { u64, ( u64 | u64 ) }):
-        v1136v1 = const u64 0
-        v4239v1 = get_elem_ptr v4133v1, __ptr { string<3> }, v1136v1, !152
-        mem_copy_val v4239v1, v4136v1
-        v1139v1 = const u64 1
-        v4241v1 = get_elem_ptr v4133v1, __ptr { u64, ( u64 | u64 ) }, v1139v1, !153
-        mem_copy_val v4241v1, v4317v1
-        v4436v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, __aggr_memcpy_02
-        mem_copy_val v4436v1, v4133v1
-        mem_copy_val v4127v1, v4436v1
-        v444v1 = const u64 1, !154
-        v4253v1 = add v4022v1, v444v1, !157
-        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v4253v1), !158
+        decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_decode_18_abi_decode_19_abi_decode_26_block5(v4443v1: __ptr { u64, ( u64 | u64 ) }):
+        v1168v1 = const u64 0
+        v4365v1 = get_elem_ptr v4259v1, __ptr { string<3> }, v1168v1, !152
+        mem_copy_val v4365v1, v4262v1
+        v1171v1 = const u64 1
+        v4367v1 = get_elem_ptr v4259v1, __ptr { u64, ( u64 | u64 ) }, v1171v1, !153
+        mem_copy_val v4367v1, v4443v1
+        v4562v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, __aggr_memcpy_02
+        mem_copy_val v4562v1, v4259v1
+        mem_copy_val v4253v1, v4562v1
+        v464v1 = const u64 1, !154
+        v4379v1 = add v4138v1, v464v1, !157
+        br decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_while(v4379v1), !158
 
         decode_script_data_0_decode_from_raw_ptr_1_abi_decode_15_abi_decode_16_end_while():
-        v1133v1 = const u64 0
-        v4120v1 = get_elem_ptr v4095v1, __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1133v1, !159
-        mem_copy_val v4120v1, v4105v1
-        v480v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, args, !160
-        mem_copy_val v480v1, v4095v1
-        v1097v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, args, !161
-        v1098v1 = const u64 0
-        v1099v1 = get_elem_ptr v1097v1, __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1098v1, !162
-        v4325v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], __tmp_arg
-        mem_copy_val v4325v1, v1099v1
-        v4373v1 = get_local __ptr { u64 }, __ret_val
-        v4374v1 = call main_32(v4325v1, v4373v1)
-        v1102v1 = get_local __ptr { u64 }, _result, !163
-        mem_copy_val v1102v1, v4373v1
-        v1121v1 = get_local __ptr { u64 }, _result, !164
-        v1112v1 = const u64 8
-        retd v1121v1 v1112v1, !168
+        v1165v1 = const u64 0
+        v4246v1 = get_elem_ptr v4221v1, __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1165v1, !159
+        mem_copy_val v4246v1, v4231v1
+        v500v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, args, !160
+        mem_copy_val v500v1, v4221v1
+        v1129v1 = get_local __ptr { [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2] }, args, !161
+        v1130v1 = const u64 0
+        v1131v1 = get_elem_ptr v1129v1, __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1130v1, !162
+        v4451v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], __tmp_arg
+        mem_copy_val v4451v1, v1131v1
+        v4499v1 = get_local __ptr { u64 }, __ret_val
+        v4500v1 = call main_32(v4451v1, v4499v1)
+        v1134v1 = get_local __ptr { u64 }, _result, !163
+        mem_copy_val v1134v1, v4499v1
+        v1153v1 = get_local __ptr { u64 }, _result, !164
+        v1144v1 = const u64 8
+        retd v1153v1 v1144v1, !168
     }
 
     entry_orig fn main_32(ops: __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], __ret_value: __ptr { u64 }) -> (), !171 {
@@ -295,431 +295,431 @@ script {
         local { { ptr, u64, u64 } } self_3
 
         entry(ops: __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], __ret_value: __ptr { u64 }):
-        v483v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_
-        mem_copy_val v483v1, ops
-        v897v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !172
-        v3687v1 = const bool false, !181
-        cbr v3687v1, encode_allow_alias_33_block0(), encode_allow_alias_33_block1(), !182
+        v503v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_
+        mem_copy_val v503v1, ops
+        v929v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !172
+        v3797v1 = const bool false, !181
+        cbr v3797v1, encode_allow_alias_33_block0(), encode_allow_alias_33_block1(), !182
 
         encode_allow_alias_33_block0():
-        v3958v1 = get_local __ptr { __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], u64 }, __tuple_init_0, !184
-        v1154v1 = const u64 0
-        v3961v1 = get_elem_ptr v3958v1, __ptr __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1154v1, !185
-        store v897v1 to v3961v1, !186
-        v1157v1 = const u64 1
-        v3963v1 = get_elem_ptr v3958v1, __ptr u64, v1157v1, !187
-        v539v1 = const u64 48
-        store v539v1 to v3963v1, !188
-        v3966v1 = get_local __ptr { __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], u64 }, __anon_00, !172
-        mem_copy_val v3966v1, v3958v1
-        v3968v1 = cast_ptr v3966v1 to __ptr slice, !172
-        v4336v1 = get_local __ptr slice, __tmp_block_arg0
-        mem_copy_val v4336v1, v3968v1
-        br encode_allow_alias_33_block2(v4336v1), !172
+        v4074v1 = get_local __ptr { __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], u64 }, __tuple_init_0, !184
+        v1186v1 = const u64 0
+        v4077v1 = get_elem_ptr v4074v1, __ptr __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], v1186v1, !185
+        store v929v1 to v4077v1, !186
+        v1189v1 = const u64 1
+        v4079v1 = get_elem_ptr v4074v1, __ptr u64, v1189v1, !187
+        v571v1 = const u64 48
+        store v571v1 to v4079v1, !188
+        v4082v1 = get_local __ptr { __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], u64 }, __anon_00, !172
+        mem_copy_val v4082v1, v4074v1
+        v4084v1 = cast_ptr v4082v1 to __ptr slice, !172
+        v4462v1 = get_local __ptr slice, __tmp_block_arg0
+        mem_copy_val v4462v1, v4084v1
+        br encode_allow_alias_33_block2(v4462v1), !172
 
         encode_allow_alias_33_block1():
-        v3728v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_00, !192
-        v840v1 = const u64 1024
-        v3729v1 = asm(cap: v840v1) -> ptr hp, !193 {
+        v3844v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_00, !192
+        v872v1 = const u64 1024
+        v3845v1 = asm(cap: v872v1) -> ptr hp, !193 {
             aloc   cap
         }
-        v3730v1 = get_local __ptr { ptr, u64, u64 }, __anon_000, !194
-        v844v1 = const u64 0
-        v3731v1 = get_elem_ptr v3730v1, __ptr ptr, v844v1, !195
-        store v3729v1 to v3731v1, !196
-        v847v1 = const u64 1
-        v3733v1 = get_elem_ptr v3730v1, __ptr u64, v847v1, !197
-        store v840v1 to v3733v1, !198
-        v850v1 = const u64 2
-        v3735v1 = get_elem_ptr v3730v1, __ptr u64, v850v1, !199
-        v842v1 = const u64 0
-        store v842v1 to v3735v1, !200
-        v4401v1 = asm(buffer: v3730v1) -> __ptr { ptr, u64, u64 } buffer {
+        v3846v1 = get_local __ptr { ptr, u64, u64 }, __anon_000, !194
+        v876v1 = const u64 0
+        v3847v1 = get_elem_ptr v3846v1, __ptr ptr, v876v1, !195
+        store v3845v1 to v3847v1, !196
+        v879v1 = const u64 1
+        v3849v1 = get_elem_ptr v3846v1, __ptr u64, v879v1, !197
+        store v872v1 to v3849v1, !198
+        v882v1 = const u64 2
+        v3851v1 = get_elem_ptr v3846v1, __ptr u64, v882v1, !199
+        v874v1 = const u64 0
+        store v874v1 to v3851v1, !200
+        v4527v1 = asm(buffer: v3846v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4446v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_0
-        mem_copy_val v4446v1, v4401v1
-        v1166v1 = const u64 0
-        v3738v1 = get_elem_ptr v3728v1, __ptr { ptr, u64, u64 }, v1166v1, !201
-        mem_copy_val v3738v1, v4446v1
-        v3742v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], self_2, !204
-        mem_copy_val v3742v1, v897v1
-        v3744v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !205
-        mem_copy_val v3744v1, v3728v1
-        v3746v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !207
-        v3748v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !209
-        mem_copy_val v3748v1, v3746v1
-        v563v1 = const u64 0, !210
-        br encode_allow_alias_33_abi_encode_46_while(v563v1), !211
+        v4572v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_0
+        mem_copy_val v4572v1, v4527v1
+        v1198v1 = const u64 0
+        v3854v1 = get_elem_ptr v3844v1, __ptr { ptr, u64, u64 }, v1198v1, !201
+        mem_copy_val v3854v1, v4572v1
+        v3858v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], self_2, !204
+        mem_copy_val v3858v1, v929v1
+        v3860v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !205
+        mem_copy_val v3860v1, v3844v1
+        v3862v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !207
+        v3864v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !209
+        mem_copy_val v3864v1, v3862v1
+        v595v1 = const u64 0, !210
+        br encode_allow_alias_33_abi_encode_46_while(v595v1), !211
 
-        encode_allow_alias_33_abi_encode_46_while(v3666v1: u64):
-        v569v1 = const u64 2
-        v3757v1 = cmp lt v3666v1 v569v1, !214
-        cbr v3757v1, encode_allow_alias_33_abi_encode_46_while_body(), encode_allow_alias_33_abi_encode_46_end_while(), !215
+        encode_allow_alias_33_abi_encode_46_while(v3776v1: u64):
+        v601v1 = const u64 2
+        v3873v1 = cmp lt v3776v1 v601v1, !214
+        cbr v3873v1, encode_allow_alias_33_abi_encode_46_while_body(), encode_allow_alias_33_abi_encode_46_end_while(), !215
 
         encode_allow_alias_33_abi_encode_46_while_body():
-        v3789v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], self_2, !217
-        v3791v1 = get_elem_ptr v3789v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v3666v1, !219
-        v3793v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !221
-        v3795v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !224
-        mem_copy_val v3795v1, v3791v1
-        v3797v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_0, !225
-        mem_copy_val v3797v1, v3793v1
-        v3799v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !227
-        v654v1 = const u64 0
-        v3800v1 = get_elem_ptr v3799v1, __ptr { string<3> }, v654v1, !229
-        v3802v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_0, !231
-        v3804v1 = get_local __ptr { string<3> }, self_000, !234
-        mem_copy_val v3804v1, v3800v1
-        v3806v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_00, !235
-        mem_copy_val v3806v1, v3802v1
-        v3808v1 = get_local __ptr { string<3> }, self_000, !237
-        v642v1 = const u64 0
-        v3809v1 = get_elem_ptr v3808v1, __ptr string<3>, v642v1, !239
-        v3811v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_00, !241
-        v3813v1 = get_local __ptr string<3>, self_0000, !244
-        mem_copy_val v3813v1, v3809v1
-        v3815v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_000, !245
-        mem_copy_val v3815v1, v3811v1
-        v3817v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_000, !247
-        v3818v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_000, !249
-        v591v1 = const u64 0
-        v3819v1 = get_elem_ptr v3818v1, __ptr { ptr, u64, u64 }, v591v1, !251
-        v4403v1 = asm(buffer: v3819v1) -> __ptr { ptr, u64, u64 } buffer {
+        v3905v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], self_2, !217
+        v3907v1 = get_elem_ptr v3905v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v3776v1, !219
+        v3909v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !221
+        v3911v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !224
+        mem_copy_val v3911v1, v3907v1
+        v3913v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_0, !225
+        mem_copy_val v3913v1, v3909v1
+        v3915v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !227
+        v686v1 = const u64 0
+        v3916v1 = get_elem_ptr v3915v1, __ptr { string<3> }, v686v1, !229
+        v3918v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_0, !231
+        v3920v1 = get_local __ptr { string<3> }, self_000, !234
+        mem_copy_val v3920v1, v3916v1
+        v3922v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_00, !235
+        mem_copy_val v3922v1, v3918v1
+        v3924v1 = get_local __ptr { string<3> }, self_000, !237
+        v674v1 = const u64 0
+        v3925v1 = get_elem_ptr v3924v1, __ptr string<3>, v674v1, !239
+        v3927v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_00, !241
+        v3929v1 = get_local __ptr string<3>, self_0000, !244
+        mem_copy_val v3929v1, v3925v1
+        v3931v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_000, !245
+        mem_copy_val v3931v1, v3927v1
+        v3933v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_000, !247
+        v3934v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_000, !249
+        v623v1 = const u64 0
+        v3935v1 = get_elem_ptr v3934v1, __ptr { ptr, u64, u64 }, v623v1, !251
+        v4529v1 = asm(buffer: v3935v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4458v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_00
-        mem_copy_val v4458v1, v4403v1
-        v3822v1 = get_local __ptr { ptr, u64, u64 }, __anon_01, !252
-        mem_copy_val v3822v1, v4458v1
-        v597v1 = const u64 0
-        v3824v1 = get_elem_ptr v3822v1, __ptr ptr, v597v1, !253
-        v3825v1 = load v3824v1, !254
-        v600v1 = const u64 1
-        v3826v1 = get_elem_ptr v3822v1, __ptr u64, v600v1, !255
-        v3827v1 = load v3826v1, !256
-        v603v1 = const u64 2
-        v3828v1 = get_elem_ptr v3822v1, __ptr u64, v603v1, !257
-        v3829v1 = load v3828v1, !258
-        v3830v1 = get_local __ptr string<3>, self_0000, !260
-        v608v1 = const u64 3
-        v3832v1 = add v3829v1, v608v1, !261
-        v3833v1 = cmp gt v3832v1 v3827v1, !262
-        cbr v3833v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block1(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3825v1, v3827v1), !263
+        v4584v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_00
+        mem_copy_val v4584v1, v4529v1
+        v3938v1 = get_local __ptr { ptr, u64, u64 }, __anon_01, !252
+        mem_copy_val v3938v1, v4584v1
+        v629v1 = const u64 0
+        v3940v1 = get_elem_ptr v3938v1, __ptr ptr, v629v1, !253
+        v3941v1 = load v3940v1, !254
+        v632v1 = const u64 1
+        v3942v1 = get_elem_ptr v3938v1, __ptr u64, v632v1, !255
+        v3943v1 = load v3942v1, !256
+        v635v1 = const u64 2
+        v3944v1 = get_elem_ptr v3938v1, __ptr u64, v635v1, !257
+        v3945v1 = load v3944v1, !258
+        v3946v1 = get_local __ptr string<3>, self_0000, !260
+        v640v1 = const u64 3
+        v3948v1 = add v3945v1, v640v1, !261
+        v3949v1 = cmp gt v3948v1 v3943v1, !262
+        cbr v3949v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block1(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3941v1, v3943v1), !263
 
-        encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3668v1: ptr, v3669v1: u64):
-        v3840v1 = get_local __ptr string<3>, __anon_10, !264
-        mem_copy_val v3840v1, v3830v1
-        v3842v1 = add v3668v1, v3829v1, !265
-        v3843v1 = cast_ptr v3842v1 to __ptr u8, !266
-        mem_copy_bytes v3843v1, v3840v1, 3, !267
-        v3846v1 = get_local __ptr { ptr, u64, u64 }, __anon_20, !268
-        v628v1 = const u64 0
-        v3847v1 = get_elem_ptr v3846v1, __ptr ptr, v628v1, !269
-        store v3668v1 to v3847v1, !270
-        v631v1 = const u64 1
-        v3849v1 = get_elem_ptr v3846v1, __ptr u64, v631v1, !271
-        store v3669v1 to v3849v1, !272
-        v634v1 = const u64 2
-        v3851v1 = get_elem_ptr v3846v1, __ptr u64, v634v1, !273
-        store v3832v1 to v3851v1, !274
-        v4405v1 = asm(buffer: v3846v1) -> __ptr { ptr, u64, u64 } buffer {
+        encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3778v1: ptr, v3779v1: u64):
+        v3956v1 = get_local __ptr string<3>, __anon_10, !264
+        mem_copy_val v3956v1, v3946v1
+        v3958v1 = add v3778v1, v3945v1, !265
+        v3959v1 = cast_ptr v3958v1 to __ptr u8, !266
+        mem_copy_bytes v3959v1, v3956v1, 3, !267
+        v3962v1 = get_local __ptr { ptr, u64, u64 }, __anon_20, !268
+        v660v1 = const u64 0
+        v3963v1 = get_elem_ptr v3962v1, __ptr ptr, v660v1, !269
+        store v3778v1 to v3963v1, !270
+        v663v1 = const u64 1
+        v3965v1 = get_elem_ptr v3962v1, __ptr u64, v663v1, !271
+        store v3779v1 to v3965v1, !272
+        v666v1 = const u64 2
+        v3967v1 = get_elem_ptr v3962v1, __ptr u64, v666v1, !273
+        store v3948v1 to v3967v1, !274
+        v4531v1 = asm(buffer: v3962v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4462v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_01
-        mem_copy_val v4462v1, v4405v1
-        v1160v1 = const u64 0
-        v3854v1 = get_elem_ptr v3817v1, __ptr { ptr, u64, u64 }, v1160v1, !275
-        mem_copy_val v3854v1, v4462v1
-        v3858v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__00, !277
-        mem_copy_val v3858v1, v3817v1
-        v3860v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__00, !279
-        v3863v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__0, !281
-        mem_copy_val v3863v1, v3860v1
-        v3865v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !283
-        v799v1 = const u64 1
-        v3866v1 = get_elem_ptr v3865v1, __ptr { u64, ( u64 | u64 ) }, v799v1, !285
-        v3868v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__0, !287
-        v3870v1 = get_local __ptr { u64, ( u64 | u64 ) }, self_100, !290
-        mem_copy_val v3870v1, v3866v1
-        v3872v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !291
-        mem_copy_val v3872v1, v3868v1
-        v3874v1 = get_local __ptr { u64, ( u64 | u64 ) }, self_100, !293
-        v3876v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !295
-        mem_copy_val v3876v1, v3874v1
-        v3878v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !296
-        v673v1 = const u64 0
-        v3879v1 = get_elem_ptr v3878v1, __ptr u64, v673v1, !297
-        v3880v1 = load v3879v1, !298
-        v676v1 = const u64 0, !292
-        v3885v1 = cmp eq v3880v1 v676v1, !301
-        cbr v3885v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block0(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block1(), !302
+        v4588v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_01
+        mem_copy_val v4588v1, v4531v1
+        v1192v1 = const u64 0
+        v3970v1 = get_elem_ptr v3933v1, __ptr { ptr, u64, u64 }, v1192v1, !275
+        mem_copy_val v3970v1, v4588v1
+        v3974v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__00, !277
+        mem_copy_val v3974v1, v3933v1
+        v3976v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__00, !279
+        v3979v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__0, !281
+        mem_copy_val v3979v1, v3976v1
+        v3981v1 = get_local __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, self_10, !283
+        v831v1 = const u64 1
+        v3982v1 = get_elem_ptr v3981v1, __ptr { u64, ( u64 | u64 ) }, v831v1, !285
+        v3984v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__0, !287
+        v3986v1 = get_local __ptr { u64, ( u64 | u64 ) }, self_100, !290
+        mem_copy_val v3986v1, v3982v1
+        v3988v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !291
+        mem_copy_val v3988v1, v3984v1
+        v3990v1 = get_local __ptr { u64, ( u64 | u64 ) }, self_100, !293
+        v3992v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !295
+        mem_copy_val v3992v1, v3990v1
+        v3994v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !296
+        v705v1 = const u64 0
+        v3995v1 = get_elem_ptr v3994v1, __ptr u64, v705v1, !297
+        v3996v1 = load v3995v1, !298
+        v708v1 = const u64 0, !292
+        v4001v1 = cmp eq v3996v1 v708v1, !301
+        cbr v4001v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block0(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block1(), !302
 
         encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block1():
-        v614v1 = const u64 2
-        v3836v1 = mul v3827v1, v614v1, !303
-        v3837v1 = add v3836v1, v608v1, !304
-        v3838v1 = asm(new_cap: v3837v1, old_ptr: v3825v1, len: v3829v1) -> __ptr u8 hp, !305 {
+        v646v1 = const u64 2
+        v3952v1 = mul v3943v1, v646v1, !303
+        v3953v1 = add v3952v1, v640v1, !304
+        v3954v1 = asm(new_cap: v3953v1, old_ptr: v3941v1, len: v3945v1) -> __ptr u8 hp, !305 {
             aloc   new_cap
             mcp    hp old_ptr len
         }
-        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3838v1, v3837v1), !306
+        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_48_abi_encode_49_block0(v3954v1, v3953v1), !306
 
         encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block0():
-        v3918v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !307
-        v679v1 = const u64 1
-        v680v1 = const u64 0
-        v3919v1 = get_elem_ptr v3918v1, __ptr u64, v679v1, v680v1, !308
-        v3920v1 = load v3919v1, !309
-        v3922v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !311
-        v4342v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg
-        mem_copy_val v4342v1, v3922v1
-        v4380v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val
-        v741v1 = const u64 0, !312
-        v4381v1 = call abi_encode_51(v741v1, v4342v1, v4380v1)
-        v3925v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__1, !314
-        mem_copy_val v3925v1, v4380v1
-        v3928v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__1, !316
-        v4345v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg0
-        mem_copy_val v4345v1, v3928v1
-        v4383v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val0
-        v4384v1 = call abi_encode_51(v3920v1, v4345v1, v4383v1)
-        v3931v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___0, !318
-        mem_copy_val v3931v1, v4383v1
-        v3933v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___0, !320
-        v4332v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_block_arg
-        mem_copy_val v4332v1, v3933v1
-        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4332v1), !321
+        v4034v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !307
+        v711v1 = const u64 1
+        v712v1 = const u64 0
+        v4035v1 = get_elem_ptr v4034v1, __ptr u64, v711v1, v712v1, !308
+        v4036v1 = load v4035v1, !309
+        v4038v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !311
+        v4468v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg
+        mem_copy_val v4468v1, v4038v1
+        v4506v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val
+        v773v1 = const u64 0, !312
+        v4507v1 = call abi_encode_51(v773v1, v4468v1, v4506v1)
+        v4041v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__1, !314
+        mem_copy_val v4041v1, v4506v1
+        v4044v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__1, !316
+        v4471v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg0
+        mem_copy_val v4471v1, v4044v1
+        v4509v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val0
+        v4510v1 = call abi_encode_51(v4036v1, v4471v1, v4509v1)
+        v4047v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___0, !318
+        mem_copy_val v4047v1, v4509v1
+        v4049v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___0, !320
+        v4458v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_block_arg
+        mem_copy_val v4458v1, v4049v1
+        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4458v1), !321
 
         encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block1():
-        v3888v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !322
-        v757v1 = const u64 0
-        v3889v1 = get_elem_ptr v3888v1, __ptr u64, v757v1, !323
-        v3890v1 = load v3889v1, !324
-        v760v1 = const u64 1, !292
-        v3895v1 = cmp eq v3890v1 v760v1, !327
-        cbr v3895v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block2(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block3(), !328
+        v4004v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !322
+        v789v1 = const u64 0
+        v4005v1 = get_elem_ptr v4004v1, __ptr u64, v789v1, !323
+        v4006v1 = load v4005v1, !324
+        v792v1 = const u64 1, !292
+        v4011v1 = cmp eq v4006v1 v792v1, !327
+        cbr v4011v1, encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block2(), encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block3(), !328
 
         encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block2():
-        v3899v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !329
-        v763v1 = const u64 1
-        v764v1 = const u64 1
-        v3900v1 = get_elem_ptr v3899v1, __ptr u64, v763v1, v764v1, !330
-        v3901v1 = load v3900v1, !331
-        v3903v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !333
-        v4348v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg1
-        mem_copy_val v4348v1, v3903v1
-        v4386v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val1
-        v769v1 = const u64 1, !334
-        v4387v1 = call abi_encode_51(v769v1, v4348v1, v4386v1)
-        v3906v1 = get_local __ptr { { ptr, u64, u64 } }, buffer____, !336
-        mem_copy_val v3906v1, v4386v1
-        v3909v1 = get_local __ptr { { ptr, u64, u64 } }, buffer____, !338
-        v4351v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg2
-        mem_copy_val v4351v1, v3909v1
-        v4389v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val2
-        v4390v1 = call abi_encode_51(v3901v1, v4351v1, v4389v1)
-        v3912v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_____, !340
-        mem_copy_val v3912v1, v4389v1
-        v3914v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_____, !342
-        v4330v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_block_arg
-        mem_copy_val v4330v1, v3914v1
-        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4330v1), !343
+        v4015v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_10, !329
+        v795v1 = const u64 1
+        v796v1 = const u64 1
+        v4016v1 = get_elem_ptr v4015v1, __ptr u64, v795v1, v796v1, !330
+        v4017v1 = load v4016v1, !331
+        v4019v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_1, !333
+        v4474v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg1
+        mem_copy_val v4474v1, v4019v1
+        v4512v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val1
+        v801v1 = const u64 1, !334
+        v4513v1 = call abi_encode_51(v801v1, v4474v1, v4512v1)
+        v4022v1 = get_local __ptr { { ptr, u64, u64 } }, buffer____, !336
+        mem_copy_val v4022v1, v4512v1
+        v4025v1 = get_local __ptr { { ptr, u64, u64 } }, buffer____, !338
+        v4477v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_arg2
+        mem_copy_val v4477v1, v4025v1
+        v4515v1 = get_local __ptr { { ptr, u64, u64 } }, __ret_val2
+        v4516v1 = call abi_encode_51(v4017v1, v4477v1, v4515v1)
+        v4028v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_____, !340
+        mem_copy_val v4028v1, v4515v1
+        v4030v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_____, !342
+        v4456v1 = get_local __ptr { { ptr, u64, u64 } }, __tmp_block_arg
+        mem_copy_val v4456v1, v4030v1
+        br encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4456v1), !343
 
         encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block3():
-        v784v1 = const u64 14757395258967588866, !294
-        revert v784v1, !344
+        v816v1 = const u64 14757395258967588866, !294
+        revert v816v1, !344
 
-        encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4328v1: __ptr { { ptr, u64, u64 } }):
-        v3936v1 = get_local __ptr { { ptr, u64, u64 } }, buffer______, !346
-        mem_copy_val v3936v1, v4328v1
-        v3938v1 = get_local __ptr { { ptr, u64, u64 } }, buffer______, !348
-        v3941v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___, !350
-        mem_copy_val v3941v1, v3938v1
-        v3943v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___, !352
-        v3946v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !354
-        mem_copy_val v3946v1, v3943v1
-        v823v1 = const u64 1, !355
-        v3953v1 = add v3666v1, v823v1, !358
-        br encode_allow_alias_33_abi_encode_46_while(v3953v1), !359
+        encode_allow_alias_33_abi_encode_46_abi_encode_47_abi_encode_50_block5(v4454v1: __ptr { { ptr, u64, u64 } }):
+        v4052v1 = get_local __ptr { { ptr, u64, u64 } }, buffer______, !346
+        mem_copy_val v4052v1, v4454v1
+        v4054v1 = get_local __ptr { { ptr, u64, u64 } }, buffer______, !348
+        v4057v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___, !350
+        mem_copy_val v4057v1, v4054v1
+        v4059v1 = get_local __ptr { { ptr, u64, u64 } }, buffer___, !352
+        v4062v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !354
+        mem_copy_val v4062v1, v4059v1
+        v855v1 = const u64 1, !355
+        v4069v1 = add v3776v1, v855v1, !358
+        br encode_allow_alias_33_abi_encode_46_while(v4069v1), !359
 
         encode_allow_alias_33_abi_encode_46_end_while():
-        v3760v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !361
-        v3763v1 = get_local __ptr { { ptr, u64, u64 } }, buffer, !363
-        mem_copy_val v3763v1, v3760v1
-        v3765v1 = get_local __ptr { { ptr, u64, u64 } }, buffer, !365
-        v3767v1 = get_local __ptr { { ptr, u64, u64 } }, self_3, !368
-        mem_copy_val v3767v1, v3765v1
-        v3769v1 = get_local __ptr { { ptr, u64, u64 } }, self_3, !370
-        v865v1 = const u64 0
-        v3770v1 = get_elem_ptr v3769v1, __ptr { ptr, u64, u64 }, v865v1, !371
-        v4407v1 = asm(buffer: v3770v1) -> __ptr { ptr, u64, u64 } buffer {
+        v3876v1 = get_local __ptr { { ptr, u64, u64 } }, buffer__, !361
+        v3879v1 = get_local __ptr { { ptr, u64, u64 } }, buffer, !363
+        mem_copy_val v3879v1, v3876v1
+        v3881v1 = get_local __ptr { { ptr, u64, u64 } }, buffer, !365
+        v3883v1 = get_local __ptr { { ptr, u64, u64 } }, self_3, !368
+        mem_copy_val v3883v1, v3881v1
+        v3885v1 = get_local __ptr { { ptr, u64, u64 } }, self_3, !370
+        v897v1 = const u64 0
+        v3886v1 = get_elem_ptr v3885v1, __ptr { ptr, u64, u64 }, v897v1, !371
+        v4533v1 = asm(buffer: v3886v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4485v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_02
-        mem_copy_val v4485v1, v4407v1
-        v3773v1 = get_local __ptr { ptr, u64, u64 }, __anon_02, !372
-        mem_copy_val v3773v1, v4485v1
-        v871v1 = const u64 0
-        v3775v1 = get_elem_ptr v3773v1, __ptr ptr, v871v1, !373
-        v877v1 = const u64 2
-        v3779v1 = get_elem_ptr v3773v1, __ptr u64, v877v1, !374
-        v3781v1 = get_local __ptr { ptr, u64 }, __anon_100, !375
-        v881v1 = const u64 0
-        v3782v1 = get_elem_ptr v3781v1, __ptr ptr, v881v1, !376
-        mem_copy_val v3782v1, v3775v1
-        v884v1 = const u64 1
-        v3784v1 = get_elem_ptr v3781v1, __ptr u64, v884v1, !377
-        mem_copy_val v3784v1, v3779v1
-        v4409v1 = asm(s: v3781v1) -> __ptr slice s {
+        v4611v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_02
+        mem_copy_val v4611v1, v4533v1
+        v3889v1 = get_local __ptr { ptr, u64, u64 }, __anon_02, !372
+        mem_copy_val v3889v1, v4611v1
+        v903v1 = const u64 0
+        v3891v1 = get_elem_ptr v3889v1, __ptr ptr, v903v1, !373
+        v909v1 = const u64 2
+        v3895v1 = get_elem_ptr v3889v1, __ptr u64, v909v1, !374
+        v3897v1 = get_local __ptr { ptr, u64 }, __anon_100, !375
+        v913v1 = const u64 0
+        v3898v1 = get_elem_ptr v3897v1, __ptr ptr, v913v1, !376
+        mem_copy_val v3898v1, v3891v1
+        v916v1 = const u64 1
+        v3900v1 = get_elem_ptr v3897v1, __ptr u64, v916v1, !377
+        mem_copy_val v3900v1, v3895v1
+        v4535v1 = asm(s: v3897v1) -> __ptr slice s {
         }
-        v4490v1 = get_local __ptr slice, __aggr_memcpy_03
-        mem_copy_val v4490v1, v4409v1
-        v4338v1 = get_local __ptr slice, __tmp_block_arg0
-        mem_copy_val v4338v1, v4490v1
-        br encode_allow_alias_33_block2(v4338v1), !172
+        v4616v1 = get_local __ptr slice, __aggr_memcpy_03
+        mem_copy_val v4616v1, v4535v1
+        v4464v1 = get_local __ptr slice, __tmp_block_arg0
+        mem_copy_val v4464v1, v4616v1
+        br encode_allow_alias_33_block2(v4464v1), !172
 
-        encode_allow_alias_33_block2(v4334v1: __ptr slice):
-        v4398v1 = get_local __ptr slice, __log_arg
-        mem_copy_val v4398v1, v4334v1
-        v899v1 = const u64 3647243719605075626
-        log __ptr slice v4398v1, v899v1
-        v980v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !378
-        v981v1 = const u64 0, !379
-        v982v1 = get_elem_ptr v980v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v981v1, !380
-        v983v1 = const u64 0
-        v984v1 = get_elem_ptr v982v1, __ptr { string<3> }, v983v1, !381
-        v985v1 = const u64 0
-        v986v1 = get_elem_ptr v984v1, __ptr string<3>, v985v1, !238
-        v989v1 = get_global __ptr string<3>, __const_global
-        v990v1 = cast_ptr v989v1 to ptr, !382
-        v992v1 = get_local __ptr { ptr, u64 }, __anon_0, !382
-        v993v1 = const u64 0
-        v994v1 = get_elem_ptr v992v1, __ptr ptr, v993v1
-        store v990v1 to v994v1, !382
-        v996v1 = const u64 1
-        v997v1 = get_elem_ptr v992v1, __ptr u64, v996v1
-        v991v1 = const u64 3
-        store v991v1 to v997v1, !382
-        v999v1 = get_local __ptr slice, __anon_1, !382
-        mem_copy_bytes v999v1, v992v1, 16
-        v4358v1 = get_local __ptr string<3>, __tmp_arg3
-        mem_copy_val v4358v1, v986v1
-        v4360v1 = get_local __ptr slice, __tmp_arg4
-        mem_copy_val v4360v1, v999v1
-        v4362v1 = call eq_str_3_57(v4358v1, v4360v1)
-        v910v1 = const bool false, !384
-        v1003v3 = cmp eq v4362v1 v910v1, !390
-        cbr v1003v3, assert_54_block0(), assert_54_block1(), !391
+        encode_allow_alias_33_block2(v4460v1: __ptr slice):
+        v4524v1 = get_local __ptr slice, __log_arg
+        mem_copy_val v4524v1, v4460v1
+        v931v1 = const u64 3647243719605075626
+        log __ptr slice v4524v1, v931v1
+        v1012v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !378
+        v1013v1 = const u64 0, !379
+        v1014v1 = get_elem_ptr v1012v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1013v1, !380
+        v1015v1 = const u64 0
+        v1016v1 = get_elem_ptr v1014v1, __ptr { string<3> }, v1015v1, !381
+        v1017v1 = const u64 0
+        v1018v1 = get_elem_ptr v1016v1, __ptr string<3>, v1017v1, !238
+        v1021v1 = get_global __ptr string<3>, __const_global
+        v1022v1 = cast_ptr v1021v1 to ptr, !382
+        v1024v1 = get_local __ptr { ptr, u64 }, __anon_0, !382
+        v1025v1 = const u64 0
+        v1026v1 = get_elem_ptr v1024v1, __ptr ptr, v1025v1
+        store v1022v1 to v1026v1, !382
+        v1028v1 = const u64 1
+        v1029v1 = get_elem_ptr v1024v1, __ptr u64, v1028v1
+        v1023v1 = const u64 3
+        store v1023v1 to v1029v1, !382
+        v1031v1 = get_local __ptr slice, __anon_1, !382
+        mem_copy_bytes v1031v1, v1024v1, 16
+        v4484v1 = get_local __ptr string<3>, __tmp_arg3
+        mem_copy_val v4484v1, v1018v1
+        v4486v1 = get_local __ptr slice, __tmp_arg4
+        mem_copy_val v4486v1, v1031v1
+        v4488v1 = call eq_str_3_57(v4484v1, v4486v1)
+        v942v1 = const bool false, !384
+        v1035v3 = cmp eq v4488v1 v942v1, !390
+        cbr v1035v3, assert_54_block0(), assert_54_block1(), !391
 
         assert_54_block0():
-        v1171v1 = const u64 18446744073709486084
-        revert v1171v1, !396
+        v1203v1 = const u64 18446744073709486084
+        revert v1203v1, !396
 
         assert_54_block1():
-        v1004v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !397
-        v1005v1 = const u64 0, !398
-        v1006v1 = get_elem_ptr v1004v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1005v1, !399
-        v1007v1 = const u64 1
-        v1008v1 = get_elem_ptr v1006v1, __ptr { u64, ( u64 | u64 ) }, v1007v1, !400
-        v1010v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !401
-        mem_copy_val v1010v1, v1008v1
-        v1012v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !402
-        v1013v1 = const u64 0
-        v1014v1 = get_elem_ptr v1012v1, __ptr u64, v1013v1, !402
-        v1015v1 = load v1014v1
-        v1016v1 = const u64 0, !402
-        v3976v1 = cmp eq v1015v1 v1016v1, !405
-        cbr v3976v1, block0(), block1(), !403
+        v1036v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !397
+        v1037v1 = const u64 0, !398
+        v1038v1 = get_elem_ptr v1036v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1037v1, !399
+        v1039v1 = const u64 1
+        v1040v1 = get_elem_ptr v1038v1, __ptr { u64, ( u64 | u64 ) }, v1039v1, !400
+        v1042v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !401
+        mem_copy_val v1042v1, v1040v1
+        v1044v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !402
+        v1045v1 = const u64 0
+        v1046v1 = get_elem_ptr v1044v1, __ptr u64, v1045v1, !402
+        v1047v1 = load v1046v1
+        v1048v1 = const u64 0, !402
+        v4092v1 = cmp eq v1047v1 v1048v1, !405
+        cbr v4092v1, block0(), block1(), !403
 
         block0():
-        v1018v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !402
-        v1019v1 = const u64 1
-        v1020v1 = const u64 0
-        v1021v1 = get_elem_ptr v1018v1, __ptr u64, v1019v1, v1020v1
-        v1022v1 = load v1021v1
-        v1033v1 = const u64 1338, !406
-        v3985v1 = cmp eq v1022v1 v1033v1, !409
-        v1035v3 = cmp eq v3985v1 v910v1, !412
-        cbr v1035v3, assert_54_block015(), assert_54_block116(), !413
+        v1050v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_1, !402
+        v1051v1 = const u64 1
+        v1052v1 = const u64 0
+        v1053v1 = get_elem_ptr v1050v1, __ptr u64, v1051v1, v1052v1
+        v1054v1 = load v1053v1
+        v1065v1 = const u64 1338, !406
+        v4101v1 = cmp eq v1054v1 v1065v1, !409
+        v1067v3 = cmp eq v4101v1 v942v1, !412
+        cbr v1067v3, assert_54_block015(), assert_54_block116(), !413
 
         assert_54_block015():
-        revert v1171v1, !414
+        revert v1203v1, !414
 
         assert_54_block116():
-        v1036v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !415
-        v1037v1 = const u64 1, !416
-        v1038v1 = get_elem_ptr v1036v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1037v1, !417
-        v1039v1 = const u64 0
-        v1040v1 = get_elem_ptr v1038v1, __ptr { string<3> }, v1039v1, !418
-        v1041v1 = const u64 0
-        v1042v1 = get_elem_ptr v1040v1, __ptr string<3>, v1041v1, !238
-        v1045v1 = get_global __ptr string<3>, __const_global0
-        v1046v1 = cast_ptr v1045v1 to ptr, !419
-        v1048v1 = get_local __ptr { ptr, u64 }, __anon_2, !419
-        v1049v1 = const u64 0
-        v1050v1 = get_elem_ptr v1048v1, __ptr ptr, v1049v1
-        store v1046v1 to v1050v1, !419
-        v1052v1 = const u64 1
-        v1053v1 = get_elem_ptr v1048v1, __ptr u64, v1052v1
-        v1047v1 = const u64 3
-        store v1047v1 to v1053v1, !419
-        v1055v1 = get_local __ptr slice, __anon_3, !419
-        mem_copy_bytes v1055v1, v1048v1, 16
-        v4363v1 = get_local __ptr string<3>, __tmp_arg5
-        mem_copy_val v4363v1, v1042v1
-        v4365v1 = get_local __ptr slice, __tmp_arg6
-        mem_copy_val v4365v1, v1055v1
-        v4367v1 = call eq_str_3_57(v4363v1, v4365v1)
-        v1059v3 = cmp eq v4367v1 v910v1, !422
-        cbr v1059v3, assert_54_block018(), assert_54_block119(), !423
+        v1068v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !415
+        v1069v1 = const u64 1, !416
+        v1070v1 = get_elem_ptr v1068v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1069v1, !417
+        v1071v1 = const u64 0
+        v1072v1 = get_elem_ptr v1070v1, __ptr { string<3> }, v1071v1, !418
+        v1073v1 = const u64 0
+        v1074v1 = get_elem_ptr v1072v1, __ptr string<3>, v1073v1, !238
+        v1077v1 = get_global __ptr string<3>, __const_global0
+        v1078v1 = cast_ptr v1077v1 to ptr, !419
+        v1080v1 = get_local __ptr { ptr, u64 }, __anon_2, !419
+        v1081v1 = const u64 0
+        v1082v1 = get_elem_ptr v1080v1, __ptr ptr, v1081v1
+        store v1078v1 to v1082v1, !419
+        v1084v1 = const u64 1
+        v1085v1 = get_elem_ptr v1080v1, __ptr u64, v1084v1
+        v1079v1 = const u64 3
+        store v1079v1 to v1085v1, !419
+        v1087v1 = get_local __ptr slice, __anon_3, !419
+        mem_copy_bytes v1087v1, v1080v1, 16
+        v4489v1 = get_local __ptr string<3>, __tmp_arg5
+        mem_copy_val v4489v1, v1074v1
+        v4491v1 = get_local __ptr slice, __tmp_arg6
+        mem_copy_val v4491v1, v1087v1
+        v4493v1 = call eq_str_3_57(v4489v1, v4491v1)
+        v1091v3 = cmp eq v4493v1 v942v1, !422
+        cbr v1091v3, assert_54_block018(), assert_54_block119(), !423
 
         assert_54_block018():
-        revert v1171v1, !424
+        revert v1203v1, !424
 
         assert_54_block119():
-        v1060v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !425
-        v1061v1 = const u64 1, !426
-        v1062v1 = get_elem_ptr v1060v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1061v1, !427
-        v1063v1 = const u64 1
-        v1064v1 = get_elem_ptr v1062v1, __ptr { u64, ( u64 | u64 ) }, v1063v1, !428
-        v1066v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !429
-        mem_copy_val v1066v1, v1064v1
-        v1068v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !430
-        v1069v1 = const u64 0
-        v1070v1 = get_elem_ptr v1068v1, __ptr u64, v1069v1, !430
-        v1071v1 = load v1070v1
-        v1072v1 = const u64 1, !430
-        v3991v1 = cmp eq v1071v1 v1072v1, !433
-        cbr v3991v1, block3(), block4(), !431
+        v1092v1 = get_local __ptr [{ { string<3> }, { u64, ( u64 | u64 ) } }; 2], ops_, !425
+        v1093v1 = const u64 1, !426
+        v1094v1 = get_elem_ptr v1092v1, __ptr { { string<3> }, { u64, ( u64 | u64 ) } }, v1093v1, !427
+        v1095v1 = const u64 1
+        v1096v1 = get_elem_ptr v1094v1, __ptr { u64, ( u64 | u64 ) }, v1095v1, !428
+        v1098v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !429
+        mem_copy_val v1098v1, v1096v1
+        v1100v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !430
+        v1101v1 = const u64 0
+        v1102v1 = get_elem_ptr v1100v1, __ptr u64, v1101v1, !430
+        v1103v1 = load v1102v1
+        v1104v1 = const u64 1, !430
+        v4107v1 = cmp eq v1103v1 v1104v1, !433
+        cbr v4107v1, block3(), block4(), !431
 
         block1():
-        v1027v1 = const u64 1, !434
-        revert v1027v1, !437
+        v1059v1 = const u64 1, !434
+        revert v1059v1, !437
 
         block3():
-        v1074v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !430
-        v1075v1 = const u64 1
-        v1076v1 = const u64 1
-        v1077v1 = get_elem_ptr v1074v1, __ptr u64, v1075v1, v1076v1
-        v1078v1 = load v1077v1
-        v1089v1 = const u64 1, !438
-        v4000v1 = cmp eq v1078v1 v1089v1, !441
-        v1091v3 = cmp eq v4000v1 v910v1, !444
-        cbr v1091v3, assert_54_block021(), assert_54_block122(), !445
+        v1106v1 = get_local __ptr { u64, ( u64 | u64 ) }, __matched_value_2, !430
+        v1107v1 = const u64 1
+        v1108v1 = const u64 1
+        v1109v1 = get_elem_ptr v1106v1, __ptr u64, v1107v1, v1108v1
+        v1110v1 = load v1109v1
+        v1121v1 = const u64 1, !438
+        v4116v1 = cmp eq v1110v1 v1121v1, !441
+        v1123v3 = cmp eq v4116v1 v942v1, !444
+        cbr v1123v3, assert_54_block021(), assert_54_block122(), !445
 
         assert_54_block021():
-        revert v1171v1, !446
+        revert v1203v1, !446
 
         assert_54_block122():
-        v1092v1 = get_local __ptr { u64 }, __struct_init_0, !447
-        v1151v1 = const u64 0
-        v1152v1 = get_elem_ptr v1092v1, __ptr u64, v1151v1, !447
-        v1093v1 = const u64 1, !448
-        store v1093v1 to v1152v1, !447
-        mem_copy_val __ret_value, v1092v1
-        v4371v1 = const unit ()
-        ret () v4371v1
+        v1124v1 = get_local __ptr { u64 }, __struct_init_0, !447
+        v1183v1 = const u64 0
+        v1184v1 = get_elem_ptr v1124v1, __ptr u64, v1183v1, !447
+        v1125v1 = const u64 1, !448
+        store v1125v1 to v1184v1, !447
+        mem_copy_val __ret_value, v1124v1
+        v4497v1 = const unit ()
+        ret () v4497v1
 
         block4():
-        v1083v1 = const u64 2, !449
-        revert v1083v1, !452
+        v1115v1 = const u64 2, !449
+        revert v1115v1, !452
     }
 
     pub fn abi_encode_51(self !453: u64, buffer: __ptr { { ptr, u64, u64 } }, __ret_value: __ptr { { ptr, u64, u64 } }) -> (), !456 {
@@ -731,66 +731,66 @@ script {
         local { { ptr, u64, u64 } } buffer_
 
         entry(self: u64, buffer: __ptr { { ptr, u64, u64 } }, __ret_value: __ptr { { ptr, u64, u64 } }):
-        v689v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_
-        mem_copy_val v689v1, buffer
-        v691v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_0, !457
-        v692v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !458
-        v693v1 = const u64 0
-        v694v1 = get_elem_ptr v692v1, __ptr { ptr, u64, u64 }, v693v1, !250
-        v4411v1 = asm(buffer: v694v1) -> __ptr { ptr, u64, u64 } buffer {
+        v721v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_
+        mem_copy_val v721v1, buffer
+        v723v1 = get_local __ptr { { ptr, u64, u64 } }, __struct_init_0, !457
+        v724v1 = get_local __ptr { { ptr, u64, u64 } }, buffer_, !458
+        v725v1 = const u64 0
+        v726v1 = get_elem_ptr v724v1, __ptr { ptr, u64, u64 }, v725v1, !250
+        v4537v1 = asm(buffer: v726v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4502v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_0
-        mem_copy_val v4502v1, v4411v1
-        v697v1 = get_local __ptr { ptr, u64, u64 }, __anon_0
-        mem_copy_val v697v1, v4502v1
-        v699v1 = const u64 0
-        v700v1 = get_elem_ptr v697v1, __ptr ptr, v699v1
-        v701v1 = load v700v1
-        v702v1 = const u64 1
-        v703v1 = get_elem_ptr v697v1, __ptr u64, v702v1
-        v704v1 = load v703v1
-        v705v1 = const u64 2
-        v706v1 = get_elem_ptr v697v1, __ptr u64, v705v1
-        v707v1 = load v706v1
-        v710v1 = const u64 8
-        v713v1 = add v707v1, v710v1
-        v714v1 = cmp gt v713v1 v704v1
-        cbr v714v1, block1(), block0(v701v1, v704v1)
+        v4628v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_0
+        mem_copy_val v4628v1, v4537v1
+        v729v1 = get_local __ptr { ptr, u64, u64 }, __anon_0
+        mem_copy_val v729v1, v4628v1
+        v731v1 = const u64 0
+        v732v1 = get_elem_ptr v729v1, __ptr ptr, v731v1
+        v733v1 = load v732v1
+        v734v1 = const u64 1
+        v735v1 = get_elem_ptr v729v1, __ptr u64, v734v1
+        v736v1 = load v735v1
+        v737v1 = const u64 2
+        v738v1 = get_elem_ptr v729v1, __ptr u64, v737v1
+        v739v1 = load v738v1
+        v742v1 = const u64 8
+        v745v1 = add v739v1, v742v1
+        v746v1 = cmp gt v745v1 v736v1
+        cbr v746v1, block1(), block0(v733v1, v736v1)
 
-        block0(v711v1: ptr, v712v1: u64):
-        v722v1 = add v711v1, v707v1
-        v723v1 = cast_ptr v722v1 to __ptr u64
-        store self to v723v1
-        v727v1 = get_local __ptr { ptr, u64, u64 }, __anon_1
-        v728v1 = const u64 0
-        v729v1 = get_elem_ptr v727v1, __ptr ptr, v728v1
-        store v711v1 to v729v1
-        v731v1 = const u64 1
-        v732v1 = get_elem_ptr v727v1, __ptr u64, v731v1
-        store v712v1 to v732v1
-        v734v1 = const u64 2
-        v735v1 = get_elem_ptr v727v1, __ptr u64, v734v1
-        store v713v1 to v735v1
-        v4413v1 = asm(buffer: v727v1) -> __ptr { ptr, u64, u64 } buffer {
+        block0(v743v1: ptr, v744v1: u64):
+        v754v1 = add v743v1, v739v1
+        v755v1 = cast_ptr v754v1 to __ptr u64
+        store self to v755v1
+        v759v1 = get_local __ptr { ptr, u64, u64 }, __anon_1
+        v760v1 = const u64 0
+        v761v1 = get_elem_ptr v759v1, __ptr ptr, v760v1
+        store v743v1 to v761v1
+        v763v1 = const u64 1
+        v764v1 = get_elem_ptr v759v1, __ptr u64, v763v1
+        store v744v1 to v764v1
+        v766v1 = const u64 2
+        v767v1 = get_elem_ptr v759v1, __ptr u64, v766v1
+        store v745v1 to v767v1
+        v4539v1 = asm(buffer: v759v1) -> __ptr { ptr, u64, u64 } buffer {
         }
-        v4505v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_00
-        mem_copy_val v4505v1, v4413v1
-        v1163v1 = const u64 0
-        v1164v1 = get_elem_ptr v691v1, __ptr { ptr, u64, u64 }, v1163v1, !457
-        mem_copy_val v1164v1, v4505v1
-        mem_copy_val __ret_value, v691v1
-        v4378v1 = const unit ()
-        ret () v4378v1
+        v4631v1 = get_local __ptr { ptr, u64, u64 }, __aggr_memcpy_00
+        mem_copy_val v4631v1, v4539v1
+        v1195v1 = const u64 0
+        v1196v1 = get_elem_ptr v723v1, __ptr { ptr, u64, u64 }, v1195v1, !457
+        mem_copy_val v1196v1, v4631v1
+        mem_copy_val __ret_value, v723v1
+        v4504v1 = const unit ()
+        ret () v4504v1
 
         block1():
-        v716v1 = const u64 2
-        v717v1 = mul v704v1, v716v1
-        v718v1 = add v717v1, v710v1
-        v719v1 = asm(new_cap: v718v1, old_ptr: v701v1, len: v707v1) -> __ptr u8 hp {
+        v748v1 = const u64 2
+        v749v1 = mul v736v1, v748v1
+        v750v1 = add v749v1, v742v1
+        v751v1 = asm(new_cap: v750v1, old_ptr: v733v1, len: v739v1) -> __ptr u8 hp {
             aloc   new_cap
             mcp    hp old_ptr len
         }
-        br block0(v719v1, v718v1)
+        br block0(v751v1, v750v1)
     }
 
     fn eq_str_3_57(a: __ptr string<3>, b: __ptr slice) -> bool, !461 {
@@ -799,36 +799,36 @@ script {
         local slice self_
 
         entry(a: __ptr string<3>, b: __ptr slice):
-        v937v1 = get_local __ptr string<3>, a_
-        mem_copy_val v937v1, a
-        v970v3 = get_local __ptr slice, self_, !464
-        mem_copy_val v970v3, b
-        v3617v1 = get_local __ptr slice, self_, !467
-        v4415v1 = asm(s: v3617v1) -> __ptr { ptr, u64 } s {
+        v969v1 = get_local __ptr string<3>, a_
+        mem_copy_val v969v1, a
+        v1002v3 = get_local __ptr slice, self_, !464
+        mem_copy_val v1002v3, b
+        v3727v1 = get_local __ptr slice, self_, !467
+        v4541v1 = asm(s: v3727v1) -> __ptr { ptr, u64 } s {
         }
-        v4515v1 = const u64 0
-        v4516v1 = get_elem_ptr v4415v1, __ptr ptr, v4515v1
-        v4517v1 = load v4516v1
-        v4518v1 = const u64 1
-        v4519v1 = get_elem_ptr v4415v1, __ptr u64, v4518v1
-        v4520v1 = load v4519v1
-        v3624v1 = get_local __ptr { ptr, u64 }, __tuple_1_, !469
-        v4537v1 = const u64 0
-        v4538v1 = get_elem_ptr v3624v1, __ptr ptr, v4537v1
-        store v4517v1 to v4538v1
-        v4540v1 = const u64 1
-        v4541v1 = get_elem_ptr v3624v1, __ptr u64, v4540v1
-        store v4520v1 to v4541v1
-        v3626v1 = get_local __ptr { ptr, u64 }, __tuple_1_, !470
-        v954v1 = const u64 0
-        v3627v1 = get_elem_ptr v3626v1, __ptr ptr, v954v1, !471
-        v3628v1 = load v3627v1, !464
-        v973v1 = get_local __ptr string<3>, a_, !472
-        v977v1 = const u64 3, !473
-        v978v1 = asm(a: v973v1, b: v3628v1, len: v977v1, r) -> bool r, !474 {
+        v4641v1 = const u64 0
+        v4642v1 = get_elem_ptr v4541v1, __ptr ptr, v4641v1
+        v4643v1 = load v4642v1
+        v4644v1 = const u64 1
+        v4645v1 = get_elem_ptr v4541v1, __ptr u64, v4644v1
+        v4646v1 = load v4645v1
+        v3734v1 = get_local __ptr { ptr, u64 }, __tuple_1_, !469
+        v4663v1 = const u64 0
+        v4664v1 = get_elem_ptr v3734v1, __ptr ptr, v4663v1
+        store v4643v1 to v4664v1
+        v4666v1 = const u64 1
+        v4667v1 = get_elem_ptr v3734v1, __ptr u64, v4666v1
+        store v4646v1 to v4667v1
+        v3736v1 = get_local __ptr { ptr, u64 }, __tuple_1_, !470
+        v986v1 = const u64 0
+        v3737v1 = get_elem_ptr v3736v1, __ptr ptr, v986v1, !471
+        v3738v1 = load v3737v1, !464
+        v1005v1 = get_local __ptr string<3>, a_, !472
+        v1009v1 = const u64 3, !473
+        v1010v1 = asm(a: v1005v1, b: v3738v1, len: v1009v1, r) -> bool r, !474 {
             meq    r a b len, !475
         }
-        ret bool v978v1
+        ret bool v1010v1
     }
 }
 
@@ -840,56 +840,56 @@ script {
 !5 = span !4 1542 1543
 !6 = span !0 80 131
 !7 = fn_call_path_span !0 80 98
-!8 = span !4 91615 91647
-!9 = fn_call_path_span !4 91615 91645
+!8 = span !4 105941 105973
+!9 = fn_call_path_span !4 105941 105971
 !10 = span !4 1525 1549
 !11 = (!6 !7 !8 !9 !10)
 !12 = (!6 !7 !8 !9 !10)
-!13 = span !4 91590 91648
-!14 = fn_call_path_span !4 91590 91609
-!15 = span !4 91463 91483
+!13 = span !4 105916 105974
+!14 = fn_call_path_span !4 105916 105935
+!15 = span !4 105789 105809
 !16 = (!6 !7 !13 !14 !15)
 !17 = (!6 !7 !13 !14 !15)
 !18 = (!6 !7 !13 !14 !15)
-!19 = span !4 91446 91484
+!19 = span !4 105772 105810
 !20 = (!6 !7 !13 !14 !19)
-!21 = span !4 91507 91513
+!21 = span !4 105833 105839
 !22 = (!6 !7 !13 !14 !21)
-!23 = span !4 91493 91514
-!24 = fn_call_path_span !4 91493 91506
-!25 = span !4 54646 54671
+!23 = span !4 105819 105840
+!24 = fn_call_path_span !4 105819 105832
+!25 = span !4 61847 61872
 !26 = (!6 !7 !13 !14 !23 !24 !25)
-!27 = span !4 54647 54668
-!28 = fn_call_path_span !4 54647 54660
-!29 = span !4 53906 53919
+!27 = span !4 61848 61869
+!28 = fn_call_path_span !4 61848 61861
+!29 = span !4 61069 61082
 !30 = (!6 !7 !13 !14 !23 !24 !27 !28 !29)
 !31 = (!6 !7 !13 !14 !23 !24 !27 !28 !29)
-!32 = span !4 53890 53920
+!32 = span !4 61053 61083
 !33 = (!6 !7 !13 !14 !23 !24 !27 !28 !32)
-!34 = span !4 54005 54010
+!34 = span !4 61168 61173
 !35 = (!6 !7 !13 !14 !23 !24 !27 !28 !34)
 !36 = (!6 !7 !13 !14 !23 !24 !27 !28)
-!37 = span !4 54034 54035
+!37 = span !4 61197 61198
 !38 = (!6 !7 !13 !14 !23 !24 !27 !28)
-!39 = span !4 54052 54057
-!40 = fn_call_path_span !4 54054 54055
+!39 = span !4 61215 61220
+!40 = fn_call_path_span !4 61217 61218
 !41 = (!6 !7 !13 !14 !23 !24 !27 !28 !39 !40)
 !42 = (!6 !7 !13 !14 !23 !24 !27 !28)
 !43 = (!6 !7 !13 !14 !23 !24 !27 !28)
-!44 = span !4 54132 54152
-!45 = fn_call_path_span !4 54139 54145
+!44 = span !4 61295 61315
+!45 = fn_call_path_span !4 61302 61308
 !46 = span !4 3466 3485
 !47 = fn_call_path_span !4 3466 3479
-!48 = span !4 54987 55033
+!48 = span !4 62245 62291
 !49 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !48)
-!50 = span !4 54988 55009
-!51 = fn_call_path_span !4 54988 55001
+!50 = span !4 62246 62267
+!51 = fn_call_path_span !4 62246 62259
 !52 = span !0 372 412
 !53 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !52)
 !54 = span !0 384 409
 !55 = fn_call_path_span !0 391 397
-!56 = span !4 53217 53237
-!57 = fn_call_path_span !4 53224 53234
+!56 = span !4 60380 60400
+!57 = fn_call_path_span !4 60387 60397
 !58 = span !4 2697 2714
 !59 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !56 !57 !58)
 !60 = span !4 625 641
@@ -906,12 +906,12 @@ script {
 !71 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !56 !57 !70)
 !72 = span !4 2817 2822
 !73 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !56 !57 !72)
-!74 = span !4 53206 53238
+!74 = span !4 60369 60401
 !75 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !74)
-!76 = span !4 53254 53258
+!76 = span !4 60417 60421
 !77 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !76)
-!78 = span !4 53254 53264
-!79 = fn_call_path_span !4 53259 53262
+!78 = span !4 60417 60427
+!79 = fn_call_path_span !4 60422 60425
 !80 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !78 !79)
 !81 = "sway-lib-std/src/raw_slice.sw"
 !82 = span !81 2922 2926
@@ -926,12 +926,12 @@ script {
 !91 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !78 !79 !90)
 !92 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !54 !55 !46 !47 !78 !79)
 !93 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !50 !51 !52)
-!94 = span !4 55011 55032
-!95 = fn_call_path_span !4 55011 55024
+!94 = span !4 62269 62290
+!95 = fn_call_path_span !4 62269 62282
 !96 = span !0 309 331
 !97 = fn_call_path_span !0 316 322
-!98 = span !4 51098 51126
-!99 = fn_call_path_span !4 51105 51117
+!98 = span !4 58261 58289
+!99 = fn_call_path_span !4 58268 58280
 !100 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !94 !95 !96 !97 !46 !47 !98 !99)
 !101 = span !4 2273 2354
 !102 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !94 !95 !96 !97 !46 !47 !98 !99 !101)
@@ -986,9 +986,9 @@ script {
 !151 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !94 !95 !150)
 !152 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !48)
 !153 = (!6 !7 !13 !14 !23 !24 !27 !28 !44 !45 !46 !47 !48)
-!154 = span !4 54171 54172
-!155 = span !4 54166 54172
-!156 = fn_call_path_span !4 54168 54170
+!154 = span !4 61334 61335
+!155 = span !4 61329 61335
+!156 = fn_call_path_span !4 61331 61333
 !157 = (!6 !7 !13 !14 !23 !24 !27 !28 !155 !156)
 !158 = (!6 !7 !13 !14 !23 !24 !27 !28)
 !159 = (!6 !7 !13 !14 !23 !24 !25)
@@ -999,30 +999,30 @@ script {
 !164 = span !0 234 241
 !165 = span !0 203 242
 !166 = fn_call_path_span !0 203 220
-!167 = span !4 49161 49187
+!167 = span !4 56324 56350
 !168 = (!165 !166 !167)
 !169 = span !114 297 695
 !170 = fn_name_span !114 300 304
 !171 = (!169 !170)
 !172 = span !114 360 363
-!173 = span !4 48742 48766
-!174 = fn_call_path_span !4 48742 48759
+!173 = span !4 55905 55929
+!174 = fn_call_path_span !4 55905 55922
 !175 = span !4 3637 3659
 !176 = fn_call_path_span !4 3637 3657
 !177 = span !4 6939 6963
 !178 = fn_call_path_span !4 6939 6956
-!179 = span !4 7838 7895
-!180 = fn_call_path_span !4 7865 7867
+!179 = span !4 7884 7941
+!180 = fn_call_path_span !4 7911 7913
 !181 = (!172 !173 !174 !175 !176 !177 !178 !175 !176 !179 !180)
 !182 = (!172 !173)
-!183 = span !4 48850 48862
+!183 = span !4 56013 56025
 !184 = (!172 !183)
 !185 = (!172 !183)
 !186 = (!172 !183)
 !187 = (!172 !183)
 !188 = (!172 !183)
-!189 = span !4 48917 48930
-!190 = fn_call_path_span !4 48917 48928
+!189 = span !4 56080 56093
+!190 = fn_call_path_span !4 56080 56091
 !191 = span !4 191 254
 !192 = (!172 !189 !190 !191)
 !193 = (!172 !189 !190)
@@ -1034,8 +1034,8 @@ script {
 !199 = (!172 !189 !190)
 !200 = (!172 !189 !190)
 !201 = (!172 !189 !190 !191)
-!202 = span !4 48898 48931
-!203 = fn_call_path_span !4 48906 48916
+!202 = span !4 56061 56094
+!203 = fn_call_path_span !4 56069 56079
 !204 = (!172 !202 !203)
 !205 = (!172 !202 !203)
 !206 = span !4 7047 7053
@@ -1058,14 +1058,14 @@ script {
 !223 = fn_call_path_span !4 7130 7140
 !224 = (!172 !202 !203 !222 !223)
 !225 = (!172 !202 !203 !222 !223)
-!226 = span !4 8031 8035
+!226 = span !4 8126 8130
 !227 = (!172 !202 !203 !222 !223 !226)
-!228 = span !4 8036 8037
+!228 = span !4 8131 8132
 !229 = (!172 !202 !203 !222 !223 !228)
-!230 = span !4 8049 8055
+!230 = span !4 8144 8150
 !231 = (!172 !202 !203 !222 !223 !230)
-!232 = span !4 8031 8056
-!233 = fn_call_path_span !4 8038 8048
+!232 = span !4 8126 8151
+!233 = fn_call_path_span !4 8133 8143
 !234 = (!172 !202 !203 !222 !223 !232 !233)
 !235 = (!172 !202 !203 !222 !223 !232 !233)
 !236 = span !0 379 383
@@ -1112,16 +1112,16 @@ script {
 !277 = (!172 !202 !203 !222 !223 !232 !233 !276)
 !278 = span !0 425 431
 !279 = (!172 !202 !203 !222 !223 !232 !233 !278)
-!280 = span !4 8018 8057
+!280 = span !4 8113 8152
 !281 = (!172 !202 !203 !222 !223 !280)
-!282 = span !4 8079 8083
+!282 = span !4 8174 8178
 !283 = (!172 !202 !203 !222 !223 !282)
-!284 = span !4 8084 8085
+!284 = span !4 8179 8180
 !285 = (!172 !202 !203 !222 !223 !284)
-!286 = span !4 8097 8103
+!286 = span !4 8192 8198
 !287 = (!172 !202 !203 !222 !223 !286)
-!288 = span !4 8079 8104
-!289 = fn_call_path_span !4 8086 8096
+!288 = span !4 8174 8199
+!289 = fn_call_path_span !4 8181 8191
 !290 = (!172 !202 !203 !222 !223 !288 !289)
 !291 = (!172 !202 !203 !222 !223 !288 !289)
 !292 = span !0 415 419
@@ -1181,9 +1181,9 @@ script {
 !346 = (!172 !202 !203 !222 !223 !288 !289 !345)
 !347 = span !0 866 872
 !348 = (!172 !202 !203 !222 !223 !288 !289 !347)
-!349 = span !4 8066 8105
+!349 = span !4 8161 8200
 !350 = (!172 !202 !203 !222 !223 !349)
-!351 = span !4 8114 8120
+!351 = span !4 8209 8215
 !352 = (!172 !202 !203 !222 !223 !351)
 !353 = span !4 7113 7148
 !354 = (!172 !202 !203 !353)
@@ -1194,12 +1194,12 @@ script {
 !359 = (!172 !202 !203)
 !360 = span !4 7190 7196
 !361 = (!172 !202 !203 !360)
-!362 = span !4 48885 48932
+!362 = span !4 56048 56095
 !363 = (!172 !362)
-!364 = span !4 48941 48947
+!364 = span !4 56104 56110
 !365 = (!172 !364)
-!366 = span !4 48941 48962
-!367 = fn_call_path_span !4 48948 48960
+!366 = span !4 56104 56125
+!367 = fn_call_path_span !4 56111 56123
 !368 = (!172 !366 !367)
 !369 = span !4 573 577
 !370 = (!172 !366 !367 !369)
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_contract/stdout.snap
```diff
@@ -8,25 +8,25 @@ output:
    Compiling library std (test/src/e2e_vm_tests/reduced_std_libs/sway-lib-std-core)
    Compiling library panicking_lib (test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_lib)
    Compiling contract panicking_contract (test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_contract)
-    Finished debug [unoptimized + fuel] target(s) [8.112 KB] in ???
+    Finished debug [unoptimized + fuel] target(s) [8.16 KB] in ???
      Running 12 tests, filtered 0 tests
 
 tested -- panicking_contract
 
-      test test_panicking_in_contract_self_impl ... ok (???, 1506 gas)
+      test test_panicking_in_contract_self_impl ... ok (???, 1507 gas)
            revert code: 828000000000000c
             ├─ panic message: panicking in contract self impl
             ├─ panicked:      in <Contract as PanickingContractAbi>::panicking_in_contract_self_impl
             │                  └─ at panicking_contract@1.2.3, src/main.sw:22:9
-      test test_directly_panicking_method ... ok (???, 2344 gas)
+      test test_directly_panicking_method ... ok (???, 2345 gas)
            revert code: 820000000000000b
             ├─ panic message: Error C.
             ├─ panic value:   C(true)
             ├─ panicked:      in <Contract as Abi>::directly_panicking_method
             │                  └─ at panicking_contract@1.2.3, src/main.sw:28:9
            decoded log values:
 C(true), log rb: 5503570629422409978
-      test test_nested_panic_inlined ... ok (???, 2843 gas)
+      test test_nested_panic_inlined ... ok (???, 2844 gas)
            revert code: 8000000000c01001
             ├─ panic message: Error E.
             ├─ panic value:   E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString { data: "in error enum variants" }])
@@ -38,7 +38,7 @@ C(true), log rb: 5503570629422409978
                                └─ at panicking_contract@1.2.3, src/main.sw:32:9
            decoded log values:
 E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString { data: "in error enum variants" }]), log rb: 5503570629422409978
-      test test_nested_panic_inlined_same_revert_code ... ok (???, 2843 gas)
+      test test_nested_panic_inlined_same_revert_code ... ok (???, 2844 gas)
            revert code: 8000000000c01001
             ├─ panic message: Error E.
             ├─ panic value:   E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString { data: "in error enum variants" }])
@@ -50,7 +50,7 @@ E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString
                                └─ at panicking_contract@1.2.3, src/main.sw:32:9
            decoded log values:
 E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString { data: "in error enum variants" }]), log rb: 5503570629422409978
-      test test_nested_panic_non_inlined ... ok (???, 2903 gas)
+      test test_nested_panic_non_inlined ... ok (???, 2904 gas)
            revert code: 8180000002804808
             ├─ panic message: Error E.
             ├─ panic value:   E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { data: "the best practice" }])
@@ -62,7 +62,7 @@ E([AsciiString { data: "to have" }, AsciiString { data: "strings" }, AsciiString
                                └─ at panicking_contract@1.2.3, src/main.sw:40:9
            decoded log values:
 E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { data: "the best practice" }]), log rb: 5503570629422409978
-      test test_nested_panic_non_inlined_same_revert_code ... ok (???, 2903 gas)
+      test test_nested_panic_non_inlined_same_revert_code ... ok (???, 2904 gas)
            revert code: 8180000002804808
             ├─ panic message: Error E.
             ├─ panic value:   E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { data: "the best practice" }])
@@ -74,7 +74,7 @@ E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { d
                                └─ at panicking_contract@1.2.3, src/main.sw:40:9
            decoded log values:
 E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { data: "the best practice" }]), log rb: 5503570629422409978
-      test test_generic_panic_with_unit ... ok (???, 1957 gas)
+      test test_generic_panic_with_unit ... ok (???, 1958 gas)
            revert code: 8100000000003806
             ├─ panic value:   ()
             ├─ panicked:      in panicking_lib::generic_panic
@@ -83,7 +83,7 @@ E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { d
                                └─ at panicking_contract@1.2.3, src/main.sw:48:9
            decoded log values:
 (), log rb: 3330666440490685604
-      test test_generic_panic_with_unit_same_revert_code ... ok (???, 1957 gas)
+      test test_generic_panic_with_unit_same_revert_code ... ok (???, 1958 gas)
            revert code: 8100000000003806
             ├─ panic value:   ()
             ├─ panicked:      in panicking_lib::generic_panic
@@ -92,7 +92,7 @@ E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { d
                                └─ at panicking_contract@1.2.3, src/main.sw:48:9
            decoded log values:
 (), log rb: 3330666440490685604
-      test test_generic_panic_with_str ... ok (???, 2175 gas)
+      test test_generic_panic_with_str ... ok (???, 2176 gas)
            revert code: 8080000000002804
             ├─ panic message: generic panic with string
             ├─ panicked:      in panicking_lib::generic_panic
@@ -101,7 +101,7 @@ E([AsciiString { data: "this" }, AsciiString { data: "is not" }, AsciiString { d
                                └─ at panicking_contract@1.2.3, src/main.sw:56:9
            decoded log values:
 AsciiString { data: "generic panic with string" }, log rb: 10098701174489624218
-      test test_generic_panic_with_different_str_same_revert_code ... ok (???, 2318 gas)
+      test test_generic_panic_with_different_str_same_revert_code ... ok (???, 2319 gas)
            revert code: 808000000000d019
             ├─ panic message: generic panic with different string
             ├─ panicked:      in panicking_lib::generic_panic
@@ -110,7 +110,7 @@ AsciiString { data: "generic panic with string" }, log rb: 10098701174489624218
                                └─ at panicking_contract@1.2.3, src/main.sw:60:9
            decoded log values:
 AsciiString { data: "generic panic with different string" }, log rb: 10098701174489624218
-      test test_generic_panic_with_error_type_enum ... ok (???, 2263 gas)
+      test test_generic_panic_with_error_type_enum ... ok (???, 2264 gas)
            revert code: 830000000000700d
             ├─ panic message: Error A.
             ├─ panic value:   A
@@ -120,7 +120,7 @@ AsciiString { data: "generic panic with different string" }, log rb: 10098701174
                                └─ at panicking_contract@1.2.3, src/main.sw:64:9
            decoded log values:
 A, log rb: 5503570629422409978
-      test test_generic_panic_with_error_type_enum_different_variant_same_revert_code ... ok (???, 2446 gas)
+      test test_generic_panic_with_error_type_enum_different_variant_same_revert_code ... ok (???, 2447 gas)
            revert code: 830000000000e01b
             ├─ panic message: Error B.
             ├─ panic value:   B(42)
```

### test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_lib/stdout.snap
```diff
@@ -7,7 +7,7 @@ output:
     Building test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_lib
    Compiling library std (test/src/e2e_vm_tests/reduced_std_libs/sway-lib-std-core)
    Compiling library panicking_lib (test/src/e2e_vm_tests/test_programs/should_pass/language/panic_expression/panicking_lib)
-    Finished debug [unoptimized + fuel] target(s) [6.616 KB] in ???
+    Finished debug [unoptimized + fuel] target(s) [6.664 KB] in ???
      Running 18 tests, filtered 0 tests
 
 tested -- panicking_lib
```

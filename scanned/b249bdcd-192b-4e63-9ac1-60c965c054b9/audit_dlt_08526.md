# [?] PLT-5498: Fix safeEncodeBits overflow (#5246)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2023-04-04
Source: https://github.com/IntersectMBO/plutus/commit/cd8bca53ed025769d1fa346dc1c768ad3bae0054
Type: security-commit

## Details
PLT-5498: Fix safeEncodeBits overflow (#5246)

Co-authored-by: Nikolaos Bezirgiannis <bezirg@users.noreply.github.com>

## Patch
### plutus-core/changelog.d/20230404_120804_bezirg_fix_safeencodebits.md
```diff
@@ -0,0 +1,3 @@
+### Fixed
+
+- Fixed the `safeEncodeBits` assertion to also guard against 1 unsafe case. Does not affect current encoding/decoding.
```

### plutus-core/plutus-core/src/PlutusCore/Flat.hs
```diff
@@ -63,12 +63,14 @@ This requires specialised encode/decode functions for each constructor
 that encodes a different number of possibilities. Here is a list of the
 tags and their used/available encoding possibilities.
 
-| Data type        | Function          | Used | Available |
-|------------------|-------------------|------|-----------|
-| default builtins | encodeBuiltin     | 47   | 128       |
-| Kinds            | encodeKind        | 2    | 2         |
-| Types            | encodeType        | 7    | 8         |
-| Terms            | encodeTerm        | 10   | 16        |
+** The BELOW table is about Typed-PLC and not UPLC. See `UntypedPlutusCore.Core.Instance.Flat`**
+
+| Data type        | Function          | Bit Width | Total | Used | Remaining |
+|------------------|-------------------|-----------|-------|------|-----------|
+| default builtins | encodeBuiltin     | 7         | 128   | 54   | 74        |
+| Kinds            | encodeKind        | 1         | 2     | 2    | 0         |
+| Types            | encodeType        | 3         | 8     | 7    | 1         |
+| Terms            | encodeTerm        | 4         | 16    | 10   | 6         |
 
 For format stability we are manually assigning the tag values to the
 constructors (and we do not use a generic algorithm that may change this order).
@@ -124,11 +126,11 @@ instance Serialise a => Flat (AsSerialize a) where
     size = size . serialise
 
 safeEncodeBits :: NumBits -> Word8 -> Encoding
-safeEncodeBits n v =
-  if 2 ^ n < v
+safeEncodeBits maxBits v =
+  if 2 ^ maxBits <= v
   then error $ "Overflow detected, cannot fit "
-               <> show v <> " in " <> show n <> " bits."
-  else eBits n v
+               <> show v <> " in " <> show maxBits <> " bits."
+  else eBits maxBits v
 
 constantWidth :: NumBits
 constantWidth = 4
```

### plutus-core/plutus-ir/src/PlutusIR/Core/Instance/Flat.hs
```diff
@@ -1,3 +1,4 @@
+{-# LANGUAGE DeriveAnyClass       #-}
 {-# LANGUAGE TypeOperators        #-}
 {-# LANGUAGE UndecidableInstances #-}
 {-# OPTIONS_GHC -Wno-orphans       #-}
@@ -18,34 +19,34 @@ the underlying representation can vary. The `Generic` instances of the
 terms can thus be used as backwards compatibility is not required.
 -}
 
-instance ( PLC.Closed uni
+deriving anyclass instance ( PLC.Closed uni
          , uni `PLC.Everywhere` Flat
          , Flat a
          , Flat tyname
          , Flat name
          ) => Flat (Datatype tyname name uni a)
 
-instance Flat Recursivity
+deriving anyclass instance Flat Recursivity
 
-instance Flat Strictness
+deriving anyclass instance Flat Strictness
 
-instance ( PLC.Closed uni
+deriving anyclass instance ( PLC.Closed uni
          , uni `PLC.Everywhere` Flat
          , Flat fun
          , Flat a
          , Flat tyname
          , Flat name
          ) => Flat (Binding tyname name uni fun a)
 
-instance ( PLC.Closed uni
+deriving anyclass instance ( PLC.Closed uni
          , uni `PLC.Everywhere` Flat
          , Flat fun
          , Flat a
          , Flat tyname
          , Flat name
          ) => Flat (Term tyname name uni fun a)
 
-instance ( PLC.Closed uni
+deriving anyclass instance ( PLC.Closed uni
          , uni `PLC.Everywhere` Flat
          , Flat fun
          , Flat a
```

### plutus-core/untyped-plutus-core/src/UntypedPlutusCore/Core/Instance/Flat.hs
```diff
@@ -52,9 +52,12 @@ This requires specialised encode/decode functions for each constructor
 that encodes a different number of possibilities. Here is a list of the
 tags and their used/available encoding possibilities.
 
-| Data type       | Function          | Used | Available |
-|-----------------|-------------------|------|-----------|
-| Terms           | encodeTerm        | 8    | 16        |
+** The BELOW table is for UPLC. **
+
+| Data type        | Function          | Bit Width | Total | Used | Remaining |
+|------------------|-------------------|-----------|-------|------|-----------|
+| default builtins | encodeBuiltin     | 7         | 128   | 54   | 74        |
+| Terms            | encodeTerm        | 4         | 16    | 8    | 8         |
 
 For format stability we are manually assigning the tag values to the
 constructors (and we do not use a generic algorithm that may change this order).
```

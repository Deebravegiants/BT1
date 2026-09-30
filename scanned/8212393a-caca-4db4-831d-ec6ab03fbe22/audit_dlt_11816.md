# [?] fix issue-887, FP reentrancy in constructor

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2022-02-10
Source: https://github.com/crytic/slither/commit/5ae6a06ed1bede6fa1c2ebb217a61c4498f68cb0
Type: security-commit

## Details
fix issue-887, FP reentrancy in constructor

## Patch
### slither/detectors/reentrancy/reentrancy.py
```diff
@@ -283,11 +283,12 @@ def _explore(self, node, visited, skip_father=None):
 
     def detect_reentrancy(self, contract):
         for function in contract.functions_and_modifiers_declared:
-            if function.is_implemented:
-                if self.KEY in function.context:
-                    continue
-                self._explore(function.entry_point, [])
-                function.context[self.KEY] = True
+            if not function.is_constructor:
+                if function.is_implemented:
+                    if self.KEY in function.context:
+                        continue
+                    self._explore(function.entry_point, [])
+                    function.context[self.KEY] = True
 
     def _detect(self):
         """"""
```

### tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol.0.4.25.ABIEncoderV2Array.json
```diff
@@ -4,19 +4,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad3",
+                    "name": "bad1",
                     "source_mapping": {
-                        "start": 1076,
-                        "length": 154,
+                        "start": 726,
+                        "length": 63,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            39,
-                            40,
-                            41
+                            29,
+                            30,
+                            31
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -136,42 +136,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad3()"
+                        "signature": "bad1(A.S[3])"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "b = abi.encode(s)",
+                    "name": "this.bad1_external(s)",
                     "source_mapping": {
-                        "start": 1195,
-                        "length": 30,
+                        "start": 763,
+                        "length": 21,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            40
+                            30
                         ],
                         "starting_column": 5,
-                        "ending_column": 35
+                        "ending_column": 26
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad3",
+                            "name": "bad1",
                             "source_mapping": {
-                                "start": 1076,
-                                "length": 154,
+                                "start": 726,
+                                "length": 63,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    39,
-                                    40,
-                                    41
+                                    29,
+                                    30,
+                                    31
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -291,16 +291,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad3()"
+                                "signature": "bad1(A.S[3])"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad3() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#39-41) trigger an abi encoding bug:\n\t- b = abi.encode(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#40)\n",
-            "markdown": "Function [A.bad3()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L39-L41) trigger an abi encoding bug:\n\t- [b = abi.encode(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L40)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L39-L41",
-            "id": "0c50cf7f7b16d965ef04035beb09d25f3fa1fa4afeeb079ea42f2db879e8f1e9",
+            "description": "Function A.bad1(A.S[3]) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#29-31) trigger an abi encoding bug:\n\t- this.bad1_external(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#30)\n",
+            "markdown": "Function [A.bad1(A.S[3])](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L29-L31) trigger an abi encoding bug:\n\t- [this.bad1_external(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L30)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L29-L31",
+            "id": "3febdd98f71332c80290c9557c5ef89ea9dbea4f520a084b0307f21b00da5010",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -309,19 +309,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad0",
+                    "name": "bad2",
                     "source_mapping": {
-                        "start": 540,
-                        "length": 61,
+                        "start": 852,
+                        "length": 160,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            21,
-                            22,
-                            23
+                            34,
+                            35,
+                            36
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -441,42 +441,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad0()"
+                        "signature": "bad2()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "this.bad0_external(bad_arr)",
+                    "name": "b = abi.encode(bad_arr)",
                     "source_mapping": {
-                        "start": 569,
-                        "length": 27,
+                        "start": 971,
+                        "length": 36,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            22
+                            35
                         ],
                         "starting_column": 5,
-                        "ending_column": 32
+                        "ending_column": 41
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad0",
+                            "name": "bad2",
                             "source_mapping": {
-                                "start": 540,
-                                "length": 61,
+                                "start": 852,
+                                "length": 160,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    21,
-                                    22,
-                                    23
+                                    34,
+                                    35,
+                                    36
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -596,16 +596,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad0()"
+                                "signature": "bad2()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad0() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#21-23) trigger an abi encoding bug:\n\t- this.bad0_external(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#22)\n",
-            "markdown": "Function [A.bad0()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L21-L23) trigger an abi encoding bug:\n\t- [this.bad0_external(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L22)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L21-L23",
-            "id": "3752da45df0ba78cc9ac01a10b398e4ad74e6ddd572764cf2f361e523a43a998",
+            "description": "Function A.bad2() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#34-36) trigger an abi encoding bug:\n\t- b = abi.encode(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#35)\n",
+            "markdown": "Function [A.bad2()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L34-L36) trigger an abi encoding bug:\n\t- [b = abi.encode(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L35)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L34-L36",
+            "id": "d5860309d331920d1e3f44508fea706df75a4a7c2e93666ca96ca00ef32d7e01",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -614,19 +614,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad1",
+                    "name": "bad3",
                     "source_mapping": {
-                        "start": 726,
-                        "length": 63,
+                        "start": 1076,
+                        "length": 154,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            29,
-                            30,
-                            31
+                            39,
+                            40,
+                            41
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -746,42 +746,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad1(A.S[3])"
+                        "signature": "bad3()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "this.bad1_external(s)",
+                    "name": "b = abi.encode(s)",
                     "source_mapping": {
-                        "start": 763,
-                        "length": 21,
+                        "start": 1195,
+                        "length": 30,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            30
+                            40
                         ],
                         "starting_column": 5,
-                        "ending_column": 26
+                        "ending_column": 35
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad1",
+                            "name": "bad3",
                             "source_mapping": {
-                                "start": 726,
-                                "length": 63,
+                                "start": 1076,
+                                "length": 154,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    29,
-                                    30,
-                                    31
+                                    39,
+                                    40,
+                                    41
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -901,16 +901,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad1(A.S[3])"
+                                "signature": "bad3()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad1(A.S[3]) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#29-31) trigger an abi encoding bug:\n\t- this.bad1_external(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#30)\n",
-            "markdown": "Function [A.bad1(A.S[3])](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L29-L31) trigger an abi encoding bug:\n\t- [this.bad1_external(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L30)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L29-L31",
-            "id": "3febdd98f71332c80290c9557c5ef89ea9dbea4f520a084b0307f21b00da5010",
+            "description": "Function A.bad3() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#39-41) trigger an abi encoding bug:\n\t- b = abi.encode(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#40)\n",
+            "markdown": "Function [A.bad3()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L39-L41) trigger an abi encoding bug:\n\t- [b = abi.encode(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L40)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L39-L41",
+            "id": "0c50cf7f7b16d965ef04035beb09d25f3fa1fa4afeeb079ea42f2db879e8f1e9",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -919,19 +919,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad5",
+                    "name": "bad0",
                     "source_mapping": {
-                        "start": 1511,
-                        "length": 142,
+                        "start": 540,
+                        "length": 61,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            49,
-                            50,
-                            51
+                            21,
+                            22,
+                            23
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1051,42 +1051,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad5()"
+                        "signature": "bad0()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "event2_bad(s)",
+                    "name": "this.bad0_external(bad_arr)",
                     "source_mapping": {
-                        "start": 1630,
-                        "length": 18,
+                        "start": 569,
+                        "length": 27,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            50
+                            22
                         ],
                         "starting_column": 5,
-                        "ending_column": 23
+                        "ending_column": 32
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad5",
+                            "name": "bad0",
                             "source_mapping": {
-                                "start": 1511,
-                                "length": 142,
+                                "start": 540,
+                                "length": 61,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    49,
-                                    50,
-                                    51
+                                    21,
+                                    22,
+                                    23
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1206,16 +1206,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad5()"
+                                "signature": "bad0()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad5() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#49-51) trigger an abi encoding bug:\n\t- event2_bad(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#50)\n",
-            "markdown": "Function [A.bad5()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L49-L51) trigger an abi encoding bug:\n\t- [event2_bad(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L50)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L49-L51",
-            "id": "e77767c95f4548636027a859ca0c63402cfb50af242f116dd3cfc5b038a4128e",
+            "description": "Function A.bad0() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#21-23) trigger an abi encoding bug:\n\t- this.bad0_external(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#22)\n",
+            "markdown": "Function [A.bad0()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L21-L23) trigger an abi encoding bug:\n\t- [this.bad0_external(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L22)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L21-L23",
+            "id": "3752da45df0ba78cc9ac01a10b398e4ad74e6ddd572764cf2f361e523a43a998",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -1224,19 +1224,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad4",
+                    "name": "bad5",
                     "source_mapping": {
-                        "start": 1296,
-                        "length": 148,
+                        "start": 1511,
+                        "length": 142,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            44,
-                            45,
-                            46
+                            49,
+                            50,
+                            51
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1356,42 +1356,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad4()"
+                        "signature": "bad5()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "event1_bad(bad_arr)",
+                    "name": "event2_bad(s)",
                     "source_mapping": {
-                        "start": 1415,
-                        "length": 24,
+                        "start": 1630,
+                        "length": 18,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            45
+                            50
                         ],
                         "starting_column": 5,
-                        "ending_column": 29
+                        "ending_column": 23
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad4",
+                            "name": "bad5",
                             "source_mapping": {
-                                "start": 1296,
-                                "length": 148,
+                                "start": 1511,
+                                "length": 142,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    44,
-                                    45,
-                                    46
+                                    49,
+                                    50,
+                                    51
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1511,16 +1511,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad4()"
+                                "signature": "bad5()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad4() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#44-46) trigger an abi encoding bug:\n\t- event1_bad(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#45)\n",
-            "markdown": "Function [A.bad4()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L44-L46) trigger an abi encoding bug:\n\t- [event1_bad(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L45)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L44-L46",
-            "id": "144c77aebb4037fe38c2864892ecb888a4fb7d5e92e321e664b2d2226658a166",
+            "description": "Function A.bad5() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#49-51) trigger an abi encoding bug:\n\t- event2_bad(s) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#50)\n",
+            "markdown": "Function [A.bad5()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L49-L51) trigger an abi encoding bug:\n\t- [event2_bad(s)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L50)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L49-L51",
+            "id": "e77767c95f4548636027a859ca0c63402cfb50af242f116dd3cfc5b038a4128e",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -1529,19 +1529,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad2",
+                    "name": "bad4",
                     "source_mapping": {
-                        "start": 852,
-                        "length": 160,
+                        "start": 1296,
+                        "length": 148,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            34,
-                            35,
-                            36
+                            44,
+                            45,
+                            46
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1661,42 +1661,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad2()"
+                        "signature": "bad4()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "b = abi.encode(bad_arr)",
+                    "name": "event1_bad(bad_arr)",
                     "source_mapping": {
-                        "start": 971,
-                        "length": 36,
+                        "start": 1415,
+                        "length": 24,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            35
+                            45
                         ],
                         "starting_column": 5,
-                        "ending_column": 41
+                        "ending_column": 29
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad2",
+                            "name": "bad4",
                             "source_mapping": {
-                                "start": 852,
-                                "length": 160,
+                                "start": 1296,
+                                "length": 148,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    34,
-                                    35,
-                                    36
+                                    44,
+                                    45,
+                                    46
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1816,16 +1816,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad2()"
+                                "signature": "bad4()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad2() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#34-36) trigger an abi encoding bug:\n\t- b = abi.encode(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#35)\n",
-            "markdown": "Function [A.bad2()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L34-L36) trigger an abi encoding bug:\n\t- [b = abi.encode(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L35)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L34-L36",
-            "id": "d5860309d331920d1e3f44508fea706df75a4a7c2e93666ca96ca00ef32d7e01",
+            "description": "Function A.bad4() (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#44-46) trigger an abi encoding bug:\n\t- event1_bad(bad_arr) (tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#45)\n",
+            "markdown": "Function [A.bad4()](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L44-L46) trigger an abi encoding bug:\n\t- [event1_bad(bad_arr)](tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L45)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.4.25/storage_ABIEncoderV2_array.sol#L44-L46",
+            "id": "144c77aebb4037fe38c2864892ecb888a4fb7d5e92e321e664b2d2226658a166",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
```

### tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol.0.5.9.ABIEncoderV2Array.json
```diff
@@ -4,19 +4,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad1",
+                    "name": "bad5",
                     "source_mapping": {
-                        "start": 744,
-                        "length": 70,
+                        "start": 1536,
+                        "length": 142,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            29,
-                            30,
-                            31
+                            49,
+                            50,
+                            51
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -136,42 +136,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad1(A.S[3])"
+                        "signature": "bad5()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "this.bad1_external(s)",
+                    "name": "event2_bad(s)",
                     "source_mapping": {
-                        "start": 788,
-                        "length": 21,
+                        "start": 1655,
+                        "length": 18,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            30
+                            50
                         ],
                         "starting_column": 5,
-                        "ending_column": 26
+                        "ending_column": 23
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad1",
+                            "name": "bad5",
                             "source_mapping": {
-                                "start": 744,
-                                "length": 70,
+                                "start": 1536,
+                                "length": 142,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    29,
-                                    30,
-                                    31
+                                    49,
+                                    50,
+                                    51
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -291,16 +291,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad1(A.S[3])"
+                                "signature": "bad5()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad1(A.S[3]) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#29-31) trigger an abi encoding bug:\n\t- this.bad1_external(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#30)\n",
-            "markdown": "Function [A.bad1(A.S[3])](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L29-L31) trigger an abi encoding bug:\n\t- [this.bad1_external(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L30)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L29-L31",
-            "id": "04f20a6b780d160f34e95fca8f1dc426e8d05eaf7a452340a809bdeafcb84efb",
+            "description": "Function A.bad5() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#49-51) trigger an abi encoding bug:\n\t- event2_bad(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#50)\n",
+            "markdown": "Function [A.bad5()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L49-L51) trigger an abi encoding bug:\n\t- [event2_bad(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L50)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L49-L51",
+            "id": "9c6da636be98419174c8e81e73efc09e7b942f9cf477cf0de793fb92c88fc976",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -309,19 +309,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad2",
+                    "name": "bad4",
                     "source_mapping": {
-                        "start": 877,
-                        "length": 160,
+                        "start": 1321,
+                        "length": 148,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            34,
-                            35,
-                            36
+                            44,
+                            45,
+                            46
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -441,42 +441,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad2()"
+                        "signature": "bad4()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "b = abi.encode(bad_arr)",
+                    "name": "event1_bad(bad_arr)",
                     "source_mapping": {
-                        "start": 996,
-                        "length": 36,
+                        "start": 1440,
+                        "length": 24,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            35
+                            45
                         ],
                         "starting_column": 5,
-                        "ending_column": 41
+                        "ending_column": 29
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad2",
+                            "name": "bad4",
                             "source_mapping": {
-                                "start": 877,
-                                "length": 160,
+                                "start": 1321,
+                                "length": 148,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    34,
-                                    35,
-                                    36
+                                    44,
+                                    45,
+                                    46
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -596,16 +596,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad2()"
+                                "signature": "bad4()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad2() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#34-36) trigger an abi encoding bug:\n\t- b = abi.encode(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#35)\n",
-            "markdown": "Function [A.bad2()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L34-L36) trigger an abi encoding bug:\n\t- [b = abi.encode(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L35)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L34-L36",
-            "id": "e976cd11118a9f5aaacfe5715cef990140fd67c7a35682446aedc878b63b3b24",
+            "description": "Function A.bad4() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#44-46) trigger an abi encoding bug:\n\t- event1_bad(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#45)\n",
+            "markdown": "Function [A.bad4()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L44-L46) trigger an abi encoding bug:\n\t- [event1_bad(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L45)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L44-L46",
+            "id": "6e9dfeb7f6ea7c989276fa8c5e27d71ab0f6b63ee878fb3f761dab9d07942246",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -614,19 +614,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad0",
+                    "name": "bad1",
                     "source_mapping": {
-                        "start": 549,
-                        "length": 61,
+                        "start": 744,
+                        "length": 70,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            21,
-                            22,
-                            23
+                            29,
+                            30,
+                            31
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -746,42 +746,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad0()"
+                        "signature": "bad1(A.S[3])"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "this.bad0_external(bad_arr)",
+                    "name": "this.bad1_external(s)",
                     "source_mapping": {
-                        "start": 578,
-                        "length": 27,
+                        "start": 788,
+                        "length": 21,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            22
+                            30
                         ],
                         "starting_column": 5,
-                        "ending_column": 32
+                        "ending_column": 26
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad0",
+                            "name": "bad1",
                             "source_mapping": {
-                                "start": 549,
-                                "length": 61,
+                                "start": 744,
+                                "length": 70,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    21,
-                                    22,
-                                    23
+                                    29,
+                                    30,
+                                    31
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -901,16 +901,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad0()"
+                                "signature": "bad1(A.S[3])"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad0() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#21-23) trigger an abi encoding bug:\n\t- this.bad0_external(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#22)\n",
-            "markdown": "Function [A.bad0()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L21-L23) trigger an abi encoding bug:\n\t- [this.bad0_external(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L22)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L21-L23",
-            "id": "4755c0ac779753117c13ea710352c179c82da332c5be5f08ea5da28efa4c63b6",
+            "description": "Function A.bad1(A.S[3]) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#29-31) trigger an abi encoding bug:\n\t- this.bad1_external(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#30)\n",
+            "markdown": "Function [A.bad1(A.S[3])](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L29-L31) trigger an abi encoding bug:\n\t- [this.bad1_external(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L30)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L29-L31",
+            "id": "04f20a6b780d160f34e95fca8f1dc426e8d05eaf7a452340a809bdeafcb84efb",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -919,19 +919,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad3",
+                    "name": "bad0",
                     "source_mapping": {
-                        "start": 1101,
-                        "length": 154,
+                        "start": 549,
+                        "length": 61,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            39,
-                            40,
-                            41
+                            21,
+                            22,
+                            23
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1051,42 +1051,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad3()"
+                        "signature": "bad0()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "b = abi.encode(s)",
+                    "name": "this.bad0_external(bad_arr)",
                     "source_mapping": {
-                        "start": 1220,
-                        "length": 30,
+                        "start": 578,
+                        "length": 27,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            40
+                            22
                         ],
                         "starting_column": 5,
-                        "ending_column": 35
+                        "ending_column": 32
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad3",
+                            "name": "bad0",
                             "source_mapping": {
-                                "start": 1101,
-                                "length": 154,
+                                "start": 549,
+                                "length": 61,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    39,
-                                    40,
-                                    41
+                                    21,
+                                    22,
+                                    23
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1206,16 +1206,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad3()"
+                                "signature": "bad0()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad3() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#39-41) trigger an abi encoding bug:\n\t- b = abi.encode(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#40)\n",
-            "markdown": "Function [A.bad3()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L39-L41) trigger an abi encoding bug:\n\t- [b = abi.encode(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L40)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L39-L41",
-            "id": "37e980d8d34fcffe10d2533052de986dd57c1d45700f02234332b275b532c71d",
+            "description": "Function A.bad0() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#21-23) trigger an abi encoding bug:\n\t- this.bad0_external(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#22)\n",
+            "markdown": "Function [A.bad0()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L21-L23) trigger an abi encoding bug:\n\t- [this.bad0_external(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L22)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L21-L23",
+            "id": "4755c0ac779753117c13ea710352c179c82da332c5be5f08ea5da28efa4c63b6",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -1224,19 +1224,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad5",
+                    "name": "bad2",
                     "source_mapping": {
-                        "start": 1536,
-                        "length": 142,
+                        "start": 877,
+                        "length": 160,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            49,
-                            50,
-                            51
+                            34,
+                            35,
+                            36
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1356,42 +1356,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad5()"
+                        "signature": "bad2()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "event2_bad(s)",
+                    "name": "b = abi.encode(bad_arr)",
                     "source_mapping": {
-                        "start": 1655,
-                        "length": 18,
+                        "start": 996,
+                        "length": 36,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            50
+                            35
                         ],
                         "starting_column": 5,
-                        "ending_column": 23
+                        "ending_column": 41
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad5",
+                            "name": "bad2",
                             "source_mapping": {
-                                "start": 1536,
-                                "length": 142,
+                                "start": 877,
+                                "length": 160,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    49,
-                                    50,
-                                    51
+                                    34,
+                                    35,
+                                    36
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1511,16 +1511,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad5()"
+                                "signature": "bad2()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad5() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#49-51) trigger an abi encoding bug:\n\t- event2_bad(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#50)\n",
-            "markdown": "Function [A.bad5()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L49-L51) trigger an abi encoding bug:\n\t- [event2_bad(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L50)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L49-L51",
-            "id": "9c6da636be98419174c8e81e73efc09e7b942f9cf477cf0de793fb92c88fc976",
+            "description": "Function A.bad2() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#34-36) trigger an abi encoding bug:\n\t- b = abi.encode(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#35)\n",
+            "markdown": "Function [A.bad2()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L34-L36) trigger an abi encoding bug:\n\t- [b = abi.encode(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L35)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L34-L36",
+            "id": "e976cd11118a9f5aaacfe5715cef990140fd67c7a35682446aedc878b63b3b24",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
@@ -1529,19 +1529,19 @@
             "elements": [
                 {
                     "type": "function",
-                    "name": "bad4",
+                    "name": "bad3",
                     "source_mapping": {
-                        "start": 1321,
-                        "length": 148,
+                        "start": 1101,
+                        "length": 154,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            44,
-                            45,
-                            46
+                            39,
+                            40,
+                            41
                         ],
                         "starting_column": 3,
                         "ending_column": 4
@@ -1661,42 +1661,42 @@
                                 "ending_column": 2
                             }
                         },
-                        "signature": "bad4()"
+                        "signature": "bad3()"
                     }
                 },
                 {
                     "type": "node",
-                    "name": "event1_bad(bad_arr)",
+                    "name": "b = abi.encode(s)",
                     "source_mapping": {
-                        "start": 1440,
-                        "length": 24,
+                        "start": 1220,
+                        "length": 30,
                         "filename_used": "/GENERIC_PATH",
                         "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "filename_absolute": "/GENERIC_PATH",
                         "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                         "is_dependency": false,
                         "lines": [
-                            45
+                            40
                         ],
                         "starting_column": 5,
-                        "ending_column": 29
+                        "ending_column": 35
                     },
                     "type_specific_fields": {
                         "parent": {
                             "type": "function",
-                            "name": "bad4",
+                            "name": "bad3",
                             "source_mapping": {
-                                "start": 1321,
-                                "length": 148,
+                                "start": 1101,
+                                "length": 154,
                                 "filename_used": "/GENERIC_PATH",
                                 "filename_relative": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "filename_absolute": "/GENERIC_PATH",
                                 "filename_short": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol",
                                 "is_dependency": false,
                                 "lines": [
-                                    44,
-                                    45,
-                                    46
+                                    39,
+                                    40,
+                                    41
                                 ],
                                 "starting_column": 3,
                                 "ending_column": 4
@@ -1816,16 +1816,16 @@
                                         "ending_column": 2
                                     }
                                 },
-                                "signature": "bad4()"
+                                "signature": "bad3()"
                             }
                         }
                     }
                 }
             ],
-            "description": "Function A.bad4() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#44-46) trigger an abi encoding bug:\n\t- event1_bad(bad_arr) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#45)\n",
-            "markdown": "Function [A.bad4()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L44-L46) trigger an abi encoding bug:\n\t- [event1_bad(bad_arr)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L45)\n",
-            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L44-L46",
-            "id": "6e9dfeb7f6ea7c989276fa8c5e27d71ab0f6b63ee878fb3f761dab9d07942246",
+            "description": "Function A.bad3() (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#39-41) trigger an abi encoding bug:\n\t- b = abi.encode(s) (tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#40)\n",
+            "markdown": "Function [A.bad3()](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L39-L41) trigger an abi encoding bug:\n\t- [b = abi.encode(s)](tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L40)\n",
+            "first_markdown_element": "tests/detectors/abiencoderv2-array/0.5.9/storage_ABIEncoderV2_array.sol#L39-L41",
+            "id": "37e980d8d34fcffe10d2533052de986dd57c1d45700f02234332b275b532c71d",
             "check": "abiencoderv2-array",
             "impact": "High",
             "confidence": "High"
```

### tests/detectors/reentrancy-benign/0.4.25/reentrancy-benign.sol
```diff
@@ -4,6 +4,15 @@ contract ReentrancyBenign {
     uint8 anotherVariableToChange;
     uint8 counter = 0;
 
+    // Should not detect reentrancy in constructor
+    constructor(address addr) {
+        (bool success) = addr.call();
+        if (!success) {
+            revert();
+        }
+        counter += 1;
+    }
+
     function bad0() public {
         if (!(msg.sender.call())) {
             revert();
```

### tests/detectors/reentrancy-benign/0.5.16/reentrancy-benign.sol
```diff
@@ -4,6 +4,15 @@ contract ReentrancyBenign {
     uint8 anotherVariableToChange;
     uint8 counter = 0;
 
+    // Should not detect reentrancy in constructor
+    constructor(address addr) public {
+        (bool success,) = addr.call("");
+        if (!success) {
+            revert();
+        }
+        counter += 1;
+    }
+
     function bad0() public {
         (bool success,) = msg.sender.call("");
         if (!success) {
```

### tests/detectors/reentrancy-benign/0.6.11/reentrancy-benign.sol
```diff
@@ -4,6 +4,15 @@ contract ReentrancyBenign {
     uint8 anotherVariableToChange;
     uint8 counter = 0;
 
+    // Should not detect reentrancy in constructor
+    constructor(address addr) public {
+        (bool success,) = addr.call("");
+        if (!success) {
+            revert();
+        }
+        counter += 1;
+    }
+
     function bad0() public {
         (bool success,) = msg.sender.call("");
         if (!success) {
```

### tests/detectors/reentrancy-benign/0.7.6/reentrancy-benign.sol
```diff
@@ -4,6 +4,15 @@ contract ReentrancyBenign {
     uint8 anotherVariableToChange;
     uint8 counter = 0;
 
+    // Should not detect reentrancy in constructor
+    constructor(address addr) {
+        (bool success,) = addr.call("");
+        if (!success) {
+            revert();
+        }
+        counter += 1;
+    }
+
     function bad0() public {
         (bool success,) = msg.sender.call("");
         if (!success) {
```

### tests/detectors/reentrancy-eth/0.4.25/reentrancy.sol
```diff
@@ -11,6 +11,16 @@ contract Reentrancy {
         userBalance[msg.sender] += msg.value;
     }   
 
+    // Should not detect reentrancy in constructor
+    constructor() public {
+        // send userBalance[msg.sender] ethers to msg.sender
+        // if mgs.sender is a contract, it will call its fallback function
+        if (!(msg.sender.call.value(userBalance[msg.sender])())) {
+            revert();
+        }
+        userBalance[msg.sender] = 0;
+    }
+
     function withdrawBalance() public{
         // send userBalance[msg.sender] ethers to msg.sender
         // if mgs.sender is a contract, it will call its fallback function
```

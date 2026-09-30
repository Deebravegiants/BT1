# [?] fix: anchor links to Vulnerability report docs (#1257)

## Summary
Severity: Unknown
Chain: Tooling
Component: crytic/slither
Published: 2022-07-26
Source: https://github.com/crytic/slither/commit/89852f0c6f4ef59e715af7acfab71b03106d7ea7
Type: security-commit

## Details
fix: anchor links to Vulnerability report docs (#1257)

* fix: incorrect anchor links to docs

## Patch
### README.md
```diff
@@ -54,7 +54,7 @@ Num | Detector | What it Detects | Impact | Confidence
 --- | --- | --- | --- | ---
 1 | `abiencoderv2-array` | [Storage abiencoderv2 array](https://github.com/crytic/slither/wiki/Detector-Documentation#storage-abiencoderv2-array) | High | High
 2 | `array-by-reference` | [Modifying storage array by value](https://github.com/crytic/slither/wiki/Detector-Documentation#modifying-storage-array-by-value) | High | High
-3 | `incorrect-shift` | [The order of parameters in a shift instruction is incorrect.](https://github.com/crytic/slither/wiki/Detector-Documentation#shift-parameter-mixup) | High | High
+3 | `incorrect-shift` | [The order of parameters in a shift instruction is incorrect.](https://github.com/crytic/slither/wiki/Detector-Documentation#incorrect-shift-in-assembly) | High | High
 4 | `multiple-constructors` | [Multiple constructor schemes](https://github.com/crytic/slither/wiki/Detector-Documentation#multiple-constructor-schemes) | High | High
 5 | `name-reused` | [Contract's name reused](https://github.com/crytic/slither/wiki/Detector-Documentation#name-reused) | High | High
 6 | `public-mappings-nested` | [Public mappings with nested variables](https://github.com/crytic/slither/wiki/Detector-Documentation#public-mappings-with-nested-variables) | High | High
@@ -124,7 +124,7 @@ Num | Detector | What it Detects | Impact | Confidence
 70 | `costly-loop` | [Costly operations in a loop](https://github.com/crytic/slither/wiki/Detector-Documentation#costly-operations-inside-a-loop) | Informational | Medium
 71 | `dead-code` | [Functions that are not used](https://github.com/crytic/slither/wiki/Detector-Documentation#dead-code) | Informational | Medium
 72 | `reentrancy-unlimited-gas` | [Reentrancy vulnerabilities through send and transfer](https://github.com/crytic/slither/wiki/Detector-Documentation#reentrancy-vulnerabilities-4) | Informational | Medium
-73 | `similar-names` | [Variable names are too similar](https://github.com/crytic/slither/wiki/Detector-Documentation#variable-names-are-too-similar) | Informational | Medium
+73 | `similar-names` | [Variable names are too similar](https://github.com/crytic/slither/wiki/Detector-Documentation#variable-names-too-similar) | Informational | Medium
 74 | `too-many-digits` | [Conformance to numeric notation best practices](https://github.com/crytic/slither/wiki/Detector-Documentation#too-many-digits) | Informational | Medium
 75 | `constable-states` | [State variables that could be declared constant](https://github.com/crytic/slither/wiki/Detector-Documentation#state-variables-that-could-be-declared-constant) | Optimization | High
 76 | `external-function` | [Public function that could be declared external](https://github.com/crytic/slither/wiki/Detector-Documentation#public-function-that-could-be-declared-external) | Optimization | High
@@ -184,7 +184,7 @@ We recommend using a Python virtual environment, as detailed in the [Developer I
 
 ### Using Docker
 
-Use the [`eth-security-toolbox`](https://github.com/trailofbits/eth-security-toolbox/) docker image. It includes all of our security tools and every major version of Solidity in a single image. `/home/share` will be mounted to `/share`  in the container.
+Use the [`eth-security-toolbox`](https://github.com/trailofbits/eth-security-toolbox/) docker image. It includes all of our security tools and every major version of Solidity in a single image. `/home/share` will be mounted to `/share` in the container.
 
 ```bash
 docker pull trailofbits/eth-security-toolbox
@@ -232,4 +232,4 @@ Title | Usage | Authors | Venue
 [SolType: Refinement Types for Arithmetic Overflow in Solidity](https://arxiv.org/abs/2110.00677) | Use Slither as frontend to build refinement type system | Bryan Tan, Benjamin Mariano, Shuvendu K. Lahiri, Isil Dillig, Yu Feng | POPL 22
 [Do Not Rug on Me: Leveraging Machine Learning Techniques for Automated Scam Detection](https://www.mdpi.com/2227-7390/10/6/949) | Use Slither to extract tokens' features (mintable, pausable, ..) | Mazorra, Bruno, Victor Adan, and Vanesa Daza | Mathematics 10.6 (2022)
 
-If you are using Slither on an academic work, consider applying to the [Crytic $10k Research Prize](https://blog.trailofbits.com/2019/11/13/announcing-the-crytic-10k-research-prize/).
+If you are using Slither on an academic work, consider applying to the [Crytic $10k Research Prize](https://blog.trailofbits.com/2019/11/13/announcing-the-crytic-10k-research-prize/).
\ No newline at end of file
```

### slither/detectors/assembly/shift_parameter_mixup.py
```diff
@@ -13,7 +13,9 @@ class ShiftParameterMixup(AbstractDetector):
     IMPACT = DetectorClassification.HIGH
     CONFIDENCE = DetectorClassification.HIGH
 
-    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#shift-parameter-mixup"
+    WIKI = (
+        "https://github.com/crytic/slither/wiki/Detector-Documentation#incorrect-shift-in-assembly"
+    )
 
     WIKI_TITLE = "Incorrect shift in assembly."
     WIKI_DESCRIPTION = "Detect if the values in a shift operation are reversed"
```

### slither/detectors/variables/similar_variables.py
```diff
@@ -17,7 +17,9 @@ class SimilarVarsDetection(AbstractDetector):
     IMPACT = DetectorClassification.INFORMATIONAL
     CONFIDENCE = DetectorClassification.MEDIUM
 
-    WIKI = "https://github.com/crytic/slither/wiki/Detector-Documentation#variable-names-are-too-similar"
+    WIKI = (
+        "https://github.com/crytic/slither/wiki/Detector-Documentation#variable-names-too-similar"
+    )
 
     WIKI_TITLE = "Variable names too similar"
     WIKI_DESCRIPTION = "Detect variables with names that are too similar."
```

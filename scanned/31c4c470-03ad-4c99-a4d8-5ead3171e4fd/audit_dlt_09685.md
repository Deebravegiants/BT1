# [?] Fixed test harness crash when actiob_traces is empty

## Summary
Severity: Unknown
Chain: EOS/Vaulta
Component: AntelopeIO/leap
Published: 2022-12-01
Source: https://github.com/AntelopeIO/leap/commit/60103935b90c1d9710dfa9e2db89806ce5f2adc4
Type: security-commit

## Details
Fixed test harness crash when actiob_traces is empty

## Patch
### tests/TestHarness/Node.py
```diff
@@ -156,6 +156,12 @@ def getTransBlockNum(trans):
         if cntxt.hasKey("processed"):
             cntxt.add("processed")
             cntxt.add("action_traces")
+            # action_traces could be empty when an exception happened in the transaction
+            # cntxt.index(0) below will crash action_traces is empty
+            cur=cntxt.getCurrent()
+            assert isinstance(cur, list), f"ERROR: action_traces is not a list."
+            if len(cur) == 0:
+                return "no_block"
             cntxt.index(0)
             if not cntxt.isSectionNull("except"):
                 return "no_block"
```

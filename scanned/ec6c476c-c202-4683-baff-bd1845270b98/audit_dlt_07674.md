# [?] integration test: fix qa issue #128: sporadic crash on rpc-integration test (#15161)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2025-05-20
Source: https://github.com/erigontech/erigon/commit/697deaa3c624077495337a1fd78e6dc6986d3e5a
Type: security-commit

## Details
integration test: fix qa issue #128: sporadic crash on rpc-integration test (#15161)

## Patch
### .github/workflows/qa-rpc-integration-tests.yml
```diff
@@ -30,7 +30,7 @@ jobs:
       - name: Checkout RPC Tests Repository & Install Requirements
         run: |
           rm -rf ${{ runner.workspace }}/rpc-tests
-          git -c advice.detachedHead=false clone --depth 1 --branch v1.58.0  https://github.com/erigontech/rpc-tests ${{runner.workspace}}/rpc-tests
+          git -c advice.detachedHead=false clone --depth 1 --branch v1.58.1  https://github.com/erigontech/rpc-tests ${{runner.workspace}}/rpc-tests
           cd ${{ runner.workspace }}/rpc-tests
           pip3 install -r requirements.txt
 
```

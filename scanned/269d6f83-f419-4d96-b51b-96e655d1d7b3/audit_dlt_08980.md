# [?] INDY-2090: Fix crash in load script due to unexpected fee aliases

## Summary
Severity: Unknown
Chain: Hyperledger Indy
Component: hyperledger-indy/indy-node
Published: 2019-05-24
Source: https://github.com/hyperledger-indy/indy-node/commit/ab88f374d90359251e7eead7cad8396216181cf4
Type: security-commit

## Details
INDY-2090: Fix crash in load script due to unexpected fee aliases

Signed-off-by: Sergey Khoroshavin <sergey.khoroshavin@dsr-corporation.com>

## Patch
### scripts/performance/perf_load/perf_client_fees.py
```diff
@@ -167,7 +167,7 @@ async def _pool_fees_init(self):
 
         type_alias_mapping = {v['fees']: k for k, v in self._auth_rule_metadata.items()}
         fees_set = json.loads(await payment.parse_get_txn_fees_response(self._payment_method, get_fees_resp))
-        self._pool_fees = {type_alias_mapping[k]: v for k, v in fees_set.items()}
+        self._pool_fees = {type_alias_mapping[k]: v for k, v in fees_set.items() if k in type_alias_mapping}
         self._logger.info("_pool_fees_init done")
 
     async def _payment_address_init(self):
```

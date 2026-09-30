# [?] merge bitcoin#27853: bugfix, fix crash error when calling `/deploymentinfo`

## Summary
Severity: Unknown
Chain: Dash
Component: dashpay/dash
Published: 2023-06-12
Source: https://github.com/dashpay/dash/commit/5b7f8704047aeb921f8d0a6652f949f05ee521fc
Type: security-commit

## Details
merge bitcoin#27853: bugfix, fix crash error when calling `/deploymentinfo`

Co-authored-by: Konstantin Akimov <github@knstqq.com>

## Patch
### src/rest.cpp
```diff
@@ -651,7 +651,7 @@ static bool rest_deploymentinfo(const CoreContext& context, HTTPRequest* req, co
                 return RESTERR(req, HTTP_BAD_REQUEST, "Block not found");
             }
 
-            jsonRequest.params.pushKV("blockhash", hash_str);
+            jsonRequest.params.push_back(hash_str);
         }
 
         req->WriteHeader("Content-Type", "application/json");
```

### test/functional/interface_rest.py
```diff
@@ -393,6 +393,10 @@ def run_test(self):
         deployment_info = self.nodes[0].getdeploymentinfo()
         assert_equal(deployment_info, self.test_rest_request('/deploymentinfo'))
 
+        previous_bb_hash = self.nodes[0].getblockhash(self.nodes[0].getblockcount() - 1)
+        deployment_info = self.nodes[0].getdeploymentinfo(previous_bb_hash)
+        assert_equal(deployment_info, self.test_rest_request(f"/deploymentinfo/{previous_bb_hash}"))
+
         non_existing_blockhash = '42759cde25462784395a337460bde75f58e73d3f08bd31fdc3507cbac856a2c4'
         resp = self.test_rest_request(f'/deploymentinfo/{non_existing_blockhash}', ret_type=RetType.OBJ, status=400)
         assert_equal(resp.read().decode('utf-8').rstrip(), "Block not found")
```

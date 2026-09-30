# [?] Add depth limit to avoid DoS attack

## Summary
Severity: Unknown
Chain: Rootstock
Component: rsksmart/rskj
Published: 2022-12-06
Source: https://github.com/rsksmart/rskj/commit/585988699128d75dd59e33bcc23c02ad76d3679a
Type: security-commit

## Details
Add depth limit to avoid DoS attack

## Patch
### rskj-core/src/main/java/co/rsk/rpc/JsonRpcRequestValidatorInterceptor.java
```diff
@@ -29,6 +29,7 @@
 
 public class JsonRpcRequestValidatorInterceptor implements JsonRpcInterceptor {
     private static final Logger logger = LoggerFactory.getLogger(JsonRpcRequestValidatorInterceptor.class);
+    private static final int MAX_JSON_REQUEST_DEPTH = 99;
 
     private final int maxBatchRequestsSize;
 
@@ -37,10 +38,12 @@ public JsonRpcRequestValidatorInterceptor(int maxBatchRequestsSize) {
     }
 
     private JsonNode getMethod(JsonNode rootNode) {
+        int depth = 0;
         JsonNode result = rootNode;
 
-        while (result.isArray() && !result.get(0).has("method")) {
+        while (depth < MAX_JSON_REQUEST_DEPTH && result.isArray() && !result.get(0).has("method")) {
             result = result.get(0);
+            depth++;
         }
 
         return result;
```

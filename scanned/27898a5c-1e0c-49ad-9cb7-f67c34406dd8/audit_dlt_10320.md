# [?] fix error handling if external query callee panicked + TestExternalQueryPanic

## Summary
Severity: Unknown
Chain: Secret
Component: scrtlabs/SecretNetwork
Published: 2020-07-15
Source: https://github.com/scrtlabs/SecretNetwork/commit/32c9516cf22f68332b5a0a15e2f41d1b743cbb3d
Type: security-commit

## Details
fix error handling if external query callee panicked + TestExternalQueryPanic

## Patch
### cosmwasm/packages/wasmi-runtime/src/wasm/query_chain.rs
```diff
@@ -127,41 +127,42 @@ pub fn encrypt_and_query_chain(
                         }
                     }
                 }
-                Ok(Err(StdError::GenericErr { msg })) => {
-                    let inner_error_bytes = base64::decode(&msg).map_err(|err| {
+                Ok(Err(StdError::GenericErr { msg })) => match base64::decode(&msg) {
+                    Err(err) => {
                         error!(
-                            "encrypt_and_query_chain() got an StdError as an answer, tried to decode the inner msg as bytes because it's encrypted, but got an error while trying to decode from base64: {:?}",
-                            err
+                            "encrypt_and_query_chain() got an StdError as an answer {:?}, tried to decode the inner msg as bytes because it's encrypted, but got an error while trying to decode from base64. This usually means that the called contract panicked and the error is plaintext: {:?}",
+                            msg, err
                         );
-                        WasmEngineError::DeserializationError
-                    })?;
-
-                    // query response returns without nonce and user_public_key appended to it
-                    // because the sender is supposed to have them already
-                    let inner_error_as_secret_msg = SecretMessage {
-                        nonce,
-                        user_public_key,
-                        msg: inner_error_bytes,
-                    };
-
-                    match inner_error_as_secret_msg.decrypt() {
-                        Err(err) => {
-                            error!(
-                                "encrypt_and_query_chain() got an error while trying to decrypt the inner error for query {:?}, stopping wasm: {:?}",
-                                String::from_utf8_lossy(&query),
-                                err
-                            );
+                        Ok(Err(StdError::GenericErr { msg }))
+                    }
+                    Ok(inner_error_bytes) => {
+                        // query response returns without nonce and user_public_key appended to it
+                        // because the sender is supposed to have them already
+                        let inner_error_as_secret_msg = SecretMessage {
+                            nonce,
+                            user_public_key,
+                            msg: inner_error_bytes,
+                        };
+
+                        match inner_error_as_secret_msg.decrypt() {
+                            Err(err) => {
+                                error!(
+                                    "encrypt_and_query_chain() got an error while trying to decrypt the inner error for query {:?}, stopping wasm: {:?}",
+                                    String::from_utf8_lossy(&query),
+                                    err
+                                );
 
-                            return Err(WasmEngineError::DecryptionError);
-                        }
-                        Ok(decrypted) => {
-                            serde_json::from_slice(&decrypted).map_err(|err| {
-                                error!("encrypt_and_query_chain() got an error while trying to deserialize the inner error as StdError: {:?}", err);
-                                WasmEngineError::DeserializationError
-                            })?
+                                return Err(WasmEngineError::DecryptionError);
+                            }
+                            Ok(decrypted) => {
+                                serde_json::from_slice(&decrypted).map_err(|err| {
+                                    error!("encrypt_and_query_chain() got an error while trying to deserialize the inner error as StdError: {:?}", err);
+                                    WasmEngineError::DeserializationError
+                                })?
+                            }
                         }
                     }
-                }
+                },
                 Ok(Err(std_error)) => {
                     error!(
                         "encrypt_and_query_chain() got an StdError as an answer, but it should be of type GenericErr and encrypted inside. Got instead: {:?}",
```

### x/compute/internal/keeper/secret_contracts_test.go
```diff
@@ -1062,3 +1062,17 @@ func TestExternalQueryWorks(t *testing.T) {
 	require.Empty(t, execErr)
 	require.Equal(t, []byte{3}, data)
 }
+
+func TestExternalQueryPanic(t *testing.T) {
+	ctx, keeper, tempDir, codeID, walletA, _ := setupTest(t, "./testdata/test-contract/contract.wasm")
+	defer os.RemoveAll(tempDir)
+
+	addr, _, err := initHelper(t, keeper, ctx, codeID, walletA, `{"nop":{}}`, true, defaultGas)
+	require.Empty(t, err)
+
+	_, _, err = execHelper(t, keeper, ctx, addr, walletA, fmt.Sprintf(`{"send_external_query_panic":{"to":"%s"}}`, addr.String()), true, defaultGas)
+
+	require.Error(t, err)
+	require.Error(t, err.GenericErr)
+	require.Equal(t, "query contract failed: Execution error: Enclave failed function call", err.GenericErr.Msg)
+}
```

### x/compute/internal/keeper/testdata/test-contract/src/contract.rs
```diff
@@ -82,6 +82,9 @@ pub enum HandleMsg {
     SendExternalQuery {
         to: HumanAddr,
     },
+    SendExternalQueryPanic {
+        to: HumanAddr,
+    },
 }
 
 #[derive(Serialize, Deserialize, Clone, Debug, PartialEq, JsonSchema)]
@@ -235,46 +238,43 @@ pub fn handle<S: Storage, A: Api, Q: Querier>(
             Ok(pass_null_pointer_to_imports_should_throw(deps, pass_type))
         }
         HandleMsg::SendExternalQuery { to } => send_external_query(deps, to),
+        HandleMsg::SendExternalQueryPanic { to } => send_external_query_panic(deps, to),
     }
 }
 
 fn send_external_query<S: Storage, A: Api, Q: Querier>(
     deps: &mut Extern<S, A, Q>,
     contract_addr: HumanAddr,
 ) -> HandleResult {
-    let answer: StdResult<u8> = deps.querier.query(&QueryRequest::Wasm(WasmQuery::Smart {
-        contract_addr,
-        msg: Binary(r#"{"receive_external_query":{"num":2}}"#.as_bytes().to_vec()),
-    }));
+    let answer: u8 = deps
+        .querier
+        .query(&QueryRequest::Wasm(WasmQuery::Smart {
+            contract_addr,
+            msg: Binary(r#"{"receive_external_query":{"num":2}}"#.as_bytes().to_vec()),
+        }))
+        .unwrap();
 
-    match answer {
-        Ok(result) => Ok(HandleResponse {
-            messages: vec![],
-            log: vec![],
-            data: Some(vec![result].into()),
-        }),
-        Err(err) => Err(err),
-    }
+    Ok(HandleResponse {
+        messages: vec![],
+        log: vec![],
+        data: Some(vec![answer].into()),
+    })
 }
 
-// fn send_external_query_contract_error<S: Storage, A: Api, Q: Querier>(
-//     deps: &mut Extern<S, A, Q>,
-//     contract_addr: HumanAddr,
-// ) -> HandleResult {
-//     let answer: String = deps
-//         .querier
-//         .query(&QueryRequest::Wasm(WasmQuery::Smart {
-//             contract_addr,
-//             msg: Binary(r#"{"receive_external_query":{"num":2}}"#.as_bytes().to_vec()),
-//         }))
-//         .unwrap();
-
-//     Ok(HandleResponse {
-//         messages: vec![],
-//         log: vec![],
-//         data: Some(Binary(answer.as_bytes().to_vec())),
-//     })
-// }
+fn send_external_query_panic<S: Storage, A: Api, Q: Querier>(
+    deps: &mut Extern<S, A, Q>,
+    contract_addr: HumanAddr,
+) -> HandleResult {
+    let err = deps
+        .querier
+        .query::<u8>(&QueryRequest::Wasm(WasmQuery::Smart {
+            contract_addr,
+            msg: Binary(r#"{"panic":{}}"#.as_bytes().to_vec()),
+        }))
+        .unwrap_err();
+
+    Err(err)
+}
 
 fn exec_callback_bad_params(contract_addr: HumanAddr) -> HandleResponse {
     HandleResponse {
```

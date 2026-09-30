# [?] [fix] #0000: Fix `panic_on_invalid_genesis.sh`

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2022-10-21
Source: https://github.com/hyperledger-iroha/iroha/commit/64078706a9ef27763a826916f38b942d9b8dfbdf
Type: security-commit

## Details
[fix] #0000: Fix `panic_on_invalid_genesis.sh`

Signed-off-by: Shanin Roman <shanin1000@yandex.ru>

## Patch
### scripts/tests/panic_on_invalid_genesis.sh
```diff
@@ -6,113 +6,19 @@ export TORII_API_URL='127.0.0.1:8084'
 export TORII_TELEMETRY_URL='127.0.0.1:8184'
 export IROHA_PUBLIC_KEY='ed01201c61faf8fe94e253b93114240394f79a607b7fa55f9e5a41ebec74b88055768b'
 export IROHA_PRIVATE_KEY='{"digest_function": "ed25519", "payload": "282ed9f3cf92811c3818dbc4ae594ed59dc1a2f78e4241e31924e101d6b1fb831c61faf8fe94e253b93114240394f79a607b7fa55f9e5a41ebec74b88055768b"}'
+export IROHA_GENESIS_ACCOUNT_PUBLIC_KEY='ed01203f4e3e98571b55514edc5ccf7e53ca7509d89b2868e62921180a6f57c2f4e255'
+export IROHA_GENESIS_ACCOUNT_PRIVATE_KEY="{ \"digest_function\": \"ed25519\", \"payload\": \"038ae16b219da35aa036335ed0a43c28a2cc737150112c78a7b8034b9d99c9023f4e3e98571b55514edc5ccf7e53ca7509d89b2868e62921180a6f57c2f4e255\" }"
 export IROHA2_CONFIG_PATH="configs/peer/config.json"
 export SUMERAGI_TRUSTED_PEERS='[{"address":"127.0.0.1:1341", "public_key": "ed01201c61faf8fe94e253b93114240394f79a607b7fa55f9e5a41ebec74b88055768b"}]'
 # Create tmp file for genesis
-export IROHA2_GENESIS_PATH="$(mktemp)" 
+export IROHA2_GENESIS_PATH="$(mktemp)"
+# Create tmp folder for block storage
+export KURA_BLOCK_STORE_PATH="$(mktemp -d)" 
 # Remove on exit
-trap 'rm -- "$IROHA2_GENESIS_PATH"' EXIT
+trap 'rm -rf -- "$IROHA2_GENESIS_PATH" "$KURA_BLOCK_STORE_PATH"' EXIT
 
 # Create invalid genesis
 # NewAssetDefinition replaced with AssetDefinition
-cat > $IROHA2_GENESIS_PATH <<- EOF
-{
-  "transactions": [
-    {
-      "isi": [
-        {
-          "Register": {
-            "object": {
-              "Raw": {
-                "Identifiable": {
-                  "NewDomain": {
-                    "id": {
-                      "name": "wonderland"
-                    },
-                    "logo": null,
-                    "metadata": {}
-                  }
-                }
-              }
-            }
-          }
-        },
-        {
-          "Register": {
-            "object": {
-              "Raw": {
-                "Identifiable": {
-                  "NewAccount": {
-                    "id": {
-                      "name": "alice",
-                      "domain_id": {
-                        "name": "wonderland"
-                      }
-                    },
-                    "signatories": [
-                      "ed01207233bfc89dcbd68c19fde6ce6158225298ec1131b6a130d1aeb454c1ab5183c0"
-                    ],
-                    "metadata": {}
-                  }
-                }
-              }
-            }
-          }
-        },
-        {
-          "Register": {
-            "object": {
-              "Raw": {
-                "Identifiable": {
-                  "AssetDefinition": {
-                    "id": {
-                      "name": "rose",
-                      "domain_id": {
-                        "name": "wonderland"
-                      }
-                    },
-                    "value_type": "Quantity",
-                    "mintable": "Infinitely",
-                    "metadata": {}
-                  }
-                }
-              }
-            }
-          }
-        },
-        {
-          "Mint": {
-            "object": {
-              "Raw": {
-                "U32": 13
-              }
-            },
-            "destination_id": {
-              "Raw": {
-                "Id": {
-                  "AssetId": {
-                    "definition_id": {
-                      "name": "rose",
-                      "domain_id": {
-                        "name": "wonderland"
-                      }
-                    },
-                    "account_id": {
-                      "name": "alice",
-                      "domain_id": {
-                        "name": "wonderland"
-                      }
-                    }
-                  }
-                }
-              }
-            }
-          }
-        }
-      ]
-    }
-  ]
-}
-EOF
+sed 's/NewAssetDefinition/AssetDefinition/' ./configs/peer/genesis.json > $IROHA2_GENESIS_PATH
 
 timeout 1m target/debug/iroha --submit-genesis 2>&1 | tee /dev/stderr | grep -q 'Transaction validation failed in genesis block'
```

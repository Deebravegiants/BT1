# [?] Unquoted variables vulnerability (#549)

## Summary
Severity: Unknown
Chain: Base
Component: base/node
Published: 2025-10-09
Source: https://github.com/base/node/commit/9124a5c7f99feaf9c14af8e929b604985da8f9f7
Type: security-commit

## Details
Unquoted variables vulnerability (#549)

## Patch
### reth/reth-entrypoint
```diff
@@ -32,10 +32,10 @@ else
     BINARY="./op-reth"
 fi
 
-mkdir -p $RETH_DATA_DIR
+mkdir -p "$RETH_DATA_DIR"
 echo "$OP_NODE_L2_ENGINE_AUTH_RAW" > "$OP_NODE_L2_ENGINE_AUTH"
 
-exec $BINARY node \
+exec "$BINARY" node \
   -vvv \
   --datadir="$RETH_DATA_DIR" \
   --log.stdout.format json \
@@ -56,7 +56,7 @@ exec $BINARY node \
   --metrics=0.0.0.0:"$METRICS_PORT" \
   --max-outbound-peers=100 \
   --chain "$RETH_CHAIN" \
-  --rollup.sequencer-http=$RETH_SEQUENCER_HTTP \
+  --rollup.sequencer-http="$RETH_SEQUENCER_HTTP" \
   --rollup.disable-tx-pool-gossip \
   --discovery.port="$DISCOVERY_PORT" \
   --port="$P2P_PORT" \
```

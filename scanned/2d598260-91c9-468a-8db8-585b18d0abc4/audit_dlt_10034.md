# [?] fix: see if the tui is causing the crash.

## Summary
Severity: Unknown
Chain: Movement
Component: movement-network/movement
Published: 2024-05-11
Source: https://github.com/movement-network/movement/commit/35cf243cda82e6cf77f4f458608542116b471f36
Type: security-commit

## Details
fix: see if the tui is causing the crash.

## Patch
### .github/workflows/m1-da-light-node.yml
```diff
@@ -15,4 +15,4 @@ jobs:
       uses: DeterminateSystems/nix-installer-action@main
 
     - name: Run test in nix environment
-      run: nix develop --command bash  -c "just m1-da-light-node test.local"  
\ No newline at end of file
+      run: nix develop --command bash  -c "just m1-da-light-node test.local -t=false"  
\ No newline at end of file
```

### .github/workflows/monza-full-node.yml
```diff
@@ -15,4 +15,4 @@ jobs:
       uses: DeterminateSystems/nix-installer-action@main
 
     - name: Run test in nix environment
-      run: nix develop --command bash  -c "just monza-full-node test.local"  
\ No newline at end of file
+      run: nix develop --command bash  -c "just monza-full-node test.local -t=false"  
\ No newline at end of file
```

### scripts/movement/run
```diff
@@ -40,5 +40,6 @@ for element in "${split[@]}"; do
     override_files+=("process-compose/$1/process-compose.$element.yml")
 done
 
+echo "Running process-compose for $1 with override files: ${override_files[@]}..."
 process-compose -f process-compose/$1/process-compose.yml "${override_files[@]}"  "${@:3}"
 cat $PC_LOG_FILE
\ No newline at end of file
```

### scripts/preludes/m1-da-light-node/prelude
```diff
@@ -2,4 +2,7 @@
 export MOVE_ROCKS_CHAIN_ID="$(openssl rand -hex 10)"
 export MOVE_ROCKS_PATH="$MOVEMENT_BASE_STORAGE_PATH/move-rocks/${MOVE_ROCKS_CHAIN_ID}/.move-rocks"
 . ./scripts/celestia/celestia-env
-cargo build -p m1-da-light-node
\ No newline at end of file
+
+echo "Building m1-da-light-node..."
+cargo build -p m1-da-light-node
+echo "Built m1-da-light-node!"
\ No newline at end of file
```

### scripts/preludes/monza-full-node/prelude
```diff
@@ -4,17 +4,27 @@ export MOVE_ROCKS_PATH="$MOVEMENT_BASE_STORAGE_PATH/move-rocks/${MOVE_ROCKS_CHAI
 . ./scripts/celestia/celestia-env
 
 # build monza
+echo "Building monza-config..."
 cargo build --bin monza-config
+echo "Built monza-config!"
+
+echo "Building m1-da-light-node..."
 cargo build -p m1-da-light-node --features "sequencer"
+echo "Built m1-da-light-node!"
+
+echo "Building monza-full-node..."
 cargo build -p monza-full-node
+echo "Built monza-full-node!"
 
 # build aptos
 WORKING_DIR=$(pwd)
 temp_dir=$MOVEMENT_BASE_STORAGE_PATH/monza-aptos
 cp -R "$MONZA_APTOS_PATH" "$temp_dir"
 chmod -R 755 $temp_dir
 cd $MOVEMENT_BASE_STORAGE_PATH/monza-aptos
+echo "Building aptos-faucet-service..."
 cargo build -p aptos-faucet-service
+echo "Built aptos-faucet-service!"
 cd $WORKING_DIR
 
 eval $(./target/debug/monza-config)
\ No newline at end of file
```

# [?] pruntime: prevent deadlock

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2020-11-16
Source: https://github.com/Phala-Network/phala-blockchain/commit/a926a18e814460c24a7525da8630bbb51d47eacf
Type: security-commit

## Details
pruntime: prevent deadlock

## Patch
### pruntime/enclave/src/lib.rs
```diff
@@ -1329,12 +1329,6 @@ fn handle_execution(state: &mut RuntimeState, pos: &TxRef,
                     contract_id: ContractId, payload: &Vec<u8>,
                     command_index: CommandIndex,
                     ecdh_privkey: &EcdhKey) {
-    let local_state = LOCAL_STATE.lock().unwrap();
-    if !local_state.dev_mode {
-        println!("Ignore one command");
-        return;
-    }
-
     let payload: types::Payload = serde_json::from_slice(payload.as_slice())
         .expect("Failed to decode payload");
     let inner_data = match payload {
@@ -1514,7 +1508,7 @@ fn dispatch_block(input: DispatchBlockReq) -> Result<Value, Value> {
             return Err(error_msg("Event was required"))
         }
 
-        parse_events(&block, &ecdh_privkey)?;
+        parse_events(&block, &ecdh_privkey, local_state.dev_mode)?;
 
         last_block = block.block_header.number;
         local_state.block_hashes.remove(0);
@@ -1533,7 +1527,7 @@ fn parse_authority_set_change(data_b64: String) -> Result<AuthoritySetChange, Va
         .map_err(|_| error_msg("cannot decode authority_set_change"))
 }
 
-fn parse_events(block_with_events: &BlockHeaderWithEvents, ecdh_privkey: &EcdhKey) -> Result<(), Value> {
+fn parse_events(block_with_events: &BlockHeaderWithEvents, ecdh_privkey: &EcdhKey, dev_mode: bool) -> Result<(), Value> {
     let ref mut state = STATE.lock().unwrap();
     let missing_field = error_msg("Missing field");
     let events = block_with_events.clone().events.ok_or(missing_field.clone())?;
@@ -1547,6 +1541,12 @@ fn parse_events(block_with_events: &BlockHeaderWithEvents, ecdh_privkey: &EcdhKe
         for evt in &evts {
             if let chain::Event::pallet_phala(pe) = &evt.event {
                 println!("pallet_phala event: {:?}", pe);
+
+                if !dev_mode {
+                    println!("skipped");
+                    continue;
+                }
+
                 if let phala::RawEvent::CommandPushed(who, contract_id, payload, num) = pe {
                     println!("push_command(contract_id: {}, payload: data[{}])", contract_id, payload.len());
                     let pos = TxRef {
```

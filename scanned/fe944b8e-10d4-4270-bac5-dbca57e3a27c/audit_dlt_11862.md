# [?] Fix schema union for one event and enum and handle race condition before  success exit

## Summary
Severity: Unknown
Chain: Indexer
Component: enviodev/hyperindex
Published: 2024-05-03
Source: https://github.com/enviodev/hyperindex/commit/b1b20e6ed96d0b24eac1f339b34c91d397288aba
Type: security-commit

## Details
Fix schema union for one event and enum and handle race condition before  success exit

## Patch
### codegenerator/cli/src/hbs_templating/codegen_templates.rs
```diff
@@ -54,6 +54,7 @@ impl HasName for EventRecordTypeTemplate {
 pub struct GraphQlEnumTypeTemplate {
     pub name: CapitalizedOptions,
     pub params: Vec<CapitalizedOptions>,
+    pub has_multiple_params: bool,
 }
 
 impl GraphQlEnumTypeTemplate {
@@ -67,10 +68,11 @@ impl GraphQlEnumTypeTemplate {
                 "Failed templating gql enum fields of enum: {}",
                 gql_enum.name
             ))?;
-
+        let has_multiple_params = params.len() > 1;
         Ok(GraphQlEnumTypeTemplate {
             name: gql_enum.name.to_capitalized_options(),
             params,
+            has_multiple_params,
         })
     }
 }
@@ -535,6 +537,7 @@ pub struct ContractTemplate {
     pub codegen_events: Vec<EventTemplate>,
     pub abi: StringifiedAbi,
     pub handler: HandlerPathsTemplate,
+    pub has_multiple_events: bool,
 }
 
 impl ContractTemplate {
@@ -554,12 +557,13 @@ impl ContractTemplate {
         let abi = contract
             .get_stringified_abi()
             .context(format!("Failed getting abi of contract {}", contract.name))?;
-
+        let has_multiple_events = contract.events.len() > 1;
         Ok(ContractTemplate {
             name,
             handler,
             codegen_events,
             abi,
+            has_multiple_events,
         })
     }
 }
@@ -658,6 +662,14 @@ impl NetworkTemplate {
 pub struct NetworkConfigTemplate {
     network_config: NetworkTemplate,
     codegen_contracts: Vec<PerNetworkContractTemplate>,
+    has_multiple_events: bool,
+}
+
+fn count_number_of_events_in_total(codegen_contracts: &Vec<PerNetworkContractTemplate>) -> usize {
+    codegen_contracts
+        .iter()
+        .map(|contract| contract.events.len())
+        .sum()
 }
 
 impl NetworkConfigTemplate {
@@ -675,9 +687,12 @@ impl NetworkConfigTemplate {
             .collect::<Result<_>>()
             .context("Failed mapping network contracts")?;
 
+        let has_multiple_events = count_number_of_events_in_total(&codegen_contracts) > 1;
+
         Ok(NetworkConfigTemplate {
             network_config,
             codegen_contracts,
+            has_multiple_events,
         })
     }
 }
```

### codegenerator/cli/templates/dynamic/codegen/src/Enums.res.hbs
```diff
@@ -4,10 +4,9 @@
 type {{enum.name.uncapitalized}} = 
 {{#each enum.params as | param | }}| @as("{{param.original}}") {{param.capitalized}}{{/each}}
 let {{enum.name.uncapitalized}}Default = {{enum.params.[0].capitalized}}
-let {{enum.name.uncapitalized}}Schema: S.t<{{enum.name.uncapitalized}}> = S.union([
+let {{enum.name.uncapitalized}}Schema: S.t<{{enum.name.uncapitalized}}> = {{#if enum.has_multiple_params}} S.union([{{/if}}
 {{#each enum.params as | param | }}
-  S.literal({{param.capitalized}}),
+  S.literal({{param.capitalized}}){{#if enum.has_multiple_params}},{{/if}}
+{{/each}}
+{{#if enum.has_multiple_params}}]){{/if}}
 {{/each}}
-])
-
-{{/each}}
\ No newline at end of file
```

### codegenerator/cli/templates/dynamic/codegen/src/Types.res.hbs
```diff
@@ -272,13 +272,13 @@ type eventName =
   | @as("{{event.event_type.truncated_for_pg_enum_limit}}") {{event.event_type.full}}
 {{/each}}
 {{/each}}
-let eventNameSchema = S.union([
+let eventNameSchema = {{#if has_multiple_events }}S.union([{{/if}}
 {{#each codegen_contracts as | contract |}}
 {{#each contract.codegen_events as | event |}}
-  S.literal({{event.event_type.full}}),
+  S.literal({{event.event_type.full}}){{#if has_multiple_events }},{{/if}}
 {{/each}}
 {{/each}}
-])
+{{#if has_multiple_events }}]){{/if}}
 
 let eventNameToString = (eventName: eventName) => switch eventName {
   {{#each codegen_contracts as | contract |}}
```

### codegenerator/cli/templates/static/codegen/src/eventFetching/ChainFetcher.res
```diff
@@ -40,6 +40,10 @@ let make = (
   }
   logger->Logging.childInfo("Initializing ChainFetcher with " ++ endpointDescription)
   let fetchState = FetchState.makeRoot(~contractAddressMapping, ~startBlock, ~endBlock)
+  let hasProcessedToEndblock = switch (latestProcessedBlock, endBlock) {
+  | (Some(latestProcessedBlock), Some(endBlock)) => latestProcessedBlock >= endBlock
+  | _ => false
+  }
   {
     logger,
     chainConfig,
@@ -48,7 +52,7 @@ let make = (
     currentBlockHeight: 0,
     isFetchingBatch: false,
     isFetchingAtHead: false,
-    hasProcessedToEndblock: false,
+    hasProcessedToEndblock,
     fetchState,
     firstEventBlockNumber,
     latestProcessedBlock,
```

### codegenerator/cli/templates/static/codegen/src/globalState/GlobalState.res
```diff
@@ -416,9 +416,13 @@ let actionReducer = (state: t, action: action) => {
       },
       [NextQuery(CheckAllChains)],
     )
-  | SuccessExit =>
-    NodeJsLocal.process->NodeJsLocal.exitWithCode(Success)
-    (state, [])
+  | SuccessExit => {
+      // delay for node exit race conditions
+      Time.resolvePromiseAfterDelay(~delayMilliseconds=4000)
+      ->Promise.thenResolve(_ => NodeJsLocal.process->NodeJsLocal.exitWithCode(Success))
+      ->ignore
+      (state, [])
+    }
   | ErrorExit(errHandler) =>
     errHandler->ErrorHandling.log
     NodeJsLocal.process->NodeJsLocal.exitWithCode(Failure)
@@ -555,7 +559,9 @@ let taskReducer = (state: t, task: task, ~dispatchAction) => {
               state.chainManager.chainFetchers,
             )
           ) {
-            dispatchAction(SuccessExit)
+            updateChainMetadataTable(state.chainManager)
+            ->Promise.thenResolve(_ => dispatchAction(SuccessExit))
+            ->ignore
           }
         }
       }
```

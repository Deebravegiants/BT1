# [?] fix: event parsing panic (#3657)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2025-04-28
Source: https://github.com/otter-sec/anchor/commit/34b6d1996b553009af6c02c230952fab16cb9596
Type: security-commit

## Details
fix: event parsing panic (#3657)

* add test

* stricter regex

* less confusing log

* even stricter regex

* add typescript fix and test

* fix

* prettier

## Patch
### client/src/lib.rs
```diff
@@ -423,7 +423,7 @@ pub fn handle_system_log(this_program_str: &str, log: &str) -> (Option<String>,
     } else if log.contains("invoke") && !log.ends_with("[1]") {
         (Some("cpi".to_string()), false) // Any string will do.
     } else {
-        let re = Regex::new(r"^Program (.*) success*$").unwrap();
+        let re = Regex::new(r"^Program ([1-9A-HJ-NP-Za-km-z]+) success$").unwrap();
         if re.is_match(log) {
             (None, true)
         } else {
@@ -441,7 +441,7 @@ impl Execution {
         let l = &logs[0];
         *logs = &logs[1..];
 
-        let re = Regex::new(r"^Program (.*) invoke.*$").unwrap();
+        let re = Regex::new(r"^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[[\d]+\]$").unwrap();
         let c = re
             .captures(l)
             .ok_or_else(|| ClientError::LogParseError(l.to_string()))?;
@@ -679,7 +679,7 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
         if let Ok(mut execution) = Execution::new(&mut logs) {
             // Create a new peekable iterator so that we can peek at the next log whilst iterating
             let mut logs_iter = logs.iter().peekable();
-            let regex = Regex::new(r"^Program (.*) invoke.*$").unwrap();
+            let regex = Regex::new(r"^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[[\d]+\]$").unwrap();
 
             while let Some(l) = logs_iter.next() {
                 // Parse the log.
@@ -868,4 +868,37 @@ mod tests {
 
         Ok(())
     }
+
+    #[test]
+    fn test_parse_logs_response_fake_pop() -> Result<()> {
+        let logs = [
+            "Program fake111111111111111111111111111111111111112 invoke [1]",
+            "Program log: i logged success",
+            "Program log: i logged success",
+            "Program fake111111111111111111111111111111111111112 consumed 1411 of 200000 compute units",
+            "Program fake111111111111111111111111111111111111112 success"
+          ];
+
+        // Converting to Vec<String> as expected in `RpcLogsResponse`
+        let logs: Vec<String> = logs.iter().map(|&l| l.to_string()).collect();
+
+        let program_id_str = "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb";
+
+        // No events returned here. Just ensuring that the function doesn't panic
+        // due an incorrectly emptied stack.
+        parse_logs_response::<MockEvent>(
+            RpcResponse {
+                context: RpcResponseContext::new(0),
+                value: RpcLogsResponse {
+                    signature: "".to_string(),
+                    err: None,
+                    logs: logs.to_vec(),
+                },
+            },
+            program_id_str,
+        )
+        .unwrap();
+
+        Ok(())
+    }
 }
```

### ts/packages/anchor/src/program/event.ts
```diff
@@ -167,6 +167,9 @@ export class EventManager {
 export class EventParser {
   private coder: Coder;
   private programId: PublicKey;
+  private static readonly INVOKE_RE =
+    /^Program ([1-9A-HJ-NP-Za-km-z]+) invoke \[(\d+)\]$/;
+  private static readonly ROOT_DEPTH = "1";
 
   constructor(programId: PublicKey, coder: Coder) {
     this.coder = coder;
@@ -184,26 +187,43 @@ export class EventParser {
   // its emission, thereby allowing us to know if a given log event was
   // emitted by *this* program. If it was, then we parse the raw string and
   // emit the event if the string matches the event being subscribed to.
-  public *parseLogs(logs: string[], errorOnDecodeFailure: boolean = false) {
-    const logScanner = new LogScanner(logs);
+  public *parseLogs(
+    logs: string[],
+    errorOnDecodeFailure = false
+  ): Generator<Event> {
+    const scanner = new LogScanner([...logs]);
     const execution = new ExecutionContext();
-    let log = logScanner.next();
-    while (log !== null) {
+
+    const firstLog = scanner.next();
+    if (firstLog === null) return;
+
+    const firstCap = EventParser.INVOKE_RE.exec(firstLog);
+    if (!firstCap || firstCap[2] !== EventParser.ROOT_DEPTH) {
+      throw new Error(`Unexpected first log line: ${firstLog}`);
+    }
+    execution.push(firstCap[1]);
+
+    while (scanner.peek() !== null) {
+      const log = scanner.next();
+      if (log === null) break;
+
       let [event, newProgram, didPop] = this.handleLog(
         execution,
         log,
         errorOnDecodeFailure
       );
-      if (event) {
-        yield event;
-      }
-      if (newProgram) {
-        execution.push(newProgram);
-      }
+
+      if (event) yield event;
+      if (newProgram) execution.push(newProgram);
+
       if (didPop) {
         execution.pop();
+        const nextLog = scanner.peek();
+        if (nextLog && nextLog.endsWith("invoke [1]")) {
+          const m = EventParser.INVOKE_RE.exec(nextLog);
+          if (m) execution.push(m[1]);
+        }
       }
-      log = logScanner.next();
     }
   }
 
@@ -254,23 +274,17 @@ export class EventParser {
 
   // Handles logs when the current program being executing is *not* this.
   private handleSystemLog(log: string): [string | null, boolean] {
-    // System component.
-    const logStart = log.split(":")[0];
-
-    // Did the program finish executing?
-    if (logStart.match(/^Program (.*) success/g) !== null) {
-      return [null, true];
-      // Recursive call.
-    } else if (
-      logStart.startsWith(`Program ${this.programId.toString()} invoke`)
-    ) {
+    if (log.startsWith(`Program ${this.programId.toString()} log:`)) {
       return [this.programId.toString(), false];
-    }
-    // CPI call.
-    else if (logStart.includes("invoke")) {
-      return ["cpi", false]; // Any string will do.
+    } else if (log.includes("invoke") && !log.endsWith("[1]")) {
+      return ["cpi", false];
     } else {
-      return [null, false];
+      let regex = /^Program ([1-9A-HJ-NP-Za-km-z]+) success$/;
+      if (regex.test(log)) {
+        return [null, true];
+      } else {
+        return [null, false];
+      }
     }
   }
 }
@@ -300,7 +314,12 @@ class ExecutionContext {
 }
 
 class LogScanner {
-  constructor(public logs: string[]) {}
+  constructor(public logs: string[]) {
+    // remove any logs that don't start with "Program "
+    // this can happen in loader logs.
+    // e.g. 3psYALQ9s7SjdezXw2kxKkVuQLtSAQxPAjETvy765EVxJE7cYqfc4oGbpNYEWsAiuXuTnqcsSUHLQ3iZUenTHTsA on devnet
+    this.logs = this.logs.filter((log) => log.startsWith("Program "));
+  }
 
   next(): string | null {
     if (this.logs.length === 0) {
@@ -310,4 +329,8 @@ class LogScanner {
     this.logs = this.logs.slice(1);
     return l;
   }
+
+  peek(): string | null {
+    return this.logs.length > 0 ? this.logs[0] : null;
+  }
 }
```

### ts/packages/anchor/tests/events.spec.ts
```diff
@@ -315,4 +315,40 @@ describe("Events", () => {
       throw new Error("Should never find logs");
     }
   });
+  it("Handles malicious log injection attempts", () => {
+    const logs = [
+      "Program fake111111111111111111111111111111111111112 invoke [1]",
+      "Program log: i logged success",
+      "Program log: i logged success",
+      "Program fake111111111111111111111111111111111111112 consumed 1411 of 200000 compute units",
+      "Program fake111111111111111111111111111111111111112 success",
+    ];
+
+    const idl: Idl = {
+      address: "Test111111111111111111111111111111111111111",
+      metadata: {
+        name: "basic_0",
+        version: "0.0.0",
+        spec: "0.1.0",
+      },
+      instructions: [
+        {
+          name: "initialize",
+          accounts: [],
+          args: [],
+          discriminator: [],
+        },
+      ],
+    };
+    const coder = new BorshCoder(idl);
+    const programId = PublicKey.default;
+    const eventParser = new EventParser(programId, coder);
+
+    // Should not find any events due to strict log parsing
+    if (Array.from(eventParser.parseLogs(logs)).length > 0) {
+      throw new Error(
+        "Should never find logs with malicious injection attempts"
+      );
+    }
+  });
 });
```

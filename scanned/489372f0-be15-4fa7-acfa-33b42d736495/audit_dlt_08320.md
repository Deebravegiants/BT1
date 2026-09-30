# [?] ts: fix program upgrade event crashes existing listeners (#1757)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2022-04-11
Source: https://github.com/otter-sec/anchor/commit/7d611ac46f9f68dd5b6b0a4f09a42c79c5268438
Type: security-commit

## Details
ts: fix program upgrade event crashes existing listeners (#1757)

## Patch
### CHANGELOG.md
```diff
@@ -25,7 +25,8 @@ The minor version will be incremented upon a breaking change and the patch versi
 * avm: `avm install` no longer downloads the version if already installed in the machine ([#1670](https://github.com/project-serum/anchor/pull/1670)).
 * cli: make `anchor test` fail when used with `--skip-deploy` option and without `--skip-local-validator` option but there already is a running validator ([#1675](https://github.com/project-serum/anchor/pull/1675)).
 * lang: Return proper error instead of panicking if account length is smaller than discriminator in functions of `(Account)Loader` ([#1678](https://github.com/project-serum/anchor/pull/1678)).
-* cli: Add `@types/bn.js` to `devDependencies` in cli template ([#1712](https://github.com/project-serum/anchor/pull/1712)). 
+* cli: Add `@types/bn.js` to `devDependencies` in cli template ([#1712](https://github.com/project-serum/anchor/pull/1712)).
+* ts: Event listener no longer crashes on Program Upgrade or any other unexpected log ([#1757](https://github.com/project-serum/anchor/pull/1757)).
 
 ### Breaking
 
```

### ts/src/program/event.ts
```diff
@@ -174,7 +174,7 @@ export class EventParser {
   // emit the event if the string matches the event being subscribed to.
   public parseLogs(logs: string[], callback: (log: Event) => void) {
     const logScanner = new LogScanner(logs);
-    const execution = new ExecutionContext(logScanner.next() as string);
+    const execution = new ExecutionContext();
     let log = logScanner.next();
     while (log !== null) {
       let [event, newProgram, didPop] = this.handleLog(execution, log);
@@ -256,17 +256,7 @@ export class EventParser {
 // Stack frame execution context, allowing one to track what program is
 // executing for a given log.
 class ExecutionContext {
-  stack: string[];
-
-  constructor(log: string) {
-    // Assumes the first log in every transaction is an `invoke` log from the
-    // runtime.
-    const program = /^Program (.*) invoke.*$/g.exec(log)?.[1];
-    if (!program) {
-      throw new Error(`Could not find program invocation log line`);
-    }
-    this.stack = [program];
-  }
+  stack: string[] = [];
 
   program(): string {
     assert.ok(this.stack.length > 0);
```

### ts/tests/events.spec.ts
```diff
@@ -3,7 +3,7 @@ import { EventParser } from "../src/program/event";
 import { BorshCoder } from "../src";
 
 describe("Events", () => {
-  it("Parses multiple instructions", async () => {
+  it("Parses multiple instructions", () => {
     const logs = [
       "Program 11111111111111111111111111111111 invoke [1]",
       "Program 11111111111111111111111111111111 success",
@@ -26,6 +26,251 @@ describe("Events", () => {
     const programId = PublicKey.default;
     const eventParser = new EventParser(programId, coder);
 
+    eventParser.parseLogs(logs, () => {
+      throw new Error("Should never find logs");
+    });
+  });
+  it("Upgrade event check", () => {
+    const logs = [
+      "Upgraded program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54",
+      "Program 11111111111111111111111111111111 invoke [1]",
+      "Program 11111111111111111111111111111111 success",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 invoke [1]",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 consumed 17867 of 200000 compute units",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 success",
+    ];
+    const idl = {
+      version: "0.0.0",
+      name: "basic_0",
+      instructions: [
+        {
+          name: "initialize",
+          accounts: [],
+          args: [],
+        },
+      ],
+    };
+    const coder = new BorshCoder(idl);
+    const programId = PublicKey.default;
+    const eventParser = new EventParser(programId, coder);
+
+    eventParser.parseLogs(logs, () => {
+      throw new Error("Should never find logs");
+    });
+  });
+  it("Find event with different start log.", (done) => {
+    const logs = [
+      "Upgraded program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 invoke [1]",
+      "Program log: Instruction: BuyNft",
+      "Program 11111111111111111111111111111111 invoke [2]",
+      "Program log: UhUxVlc2hGeTBjNPCGmmZjvNSuBOYpfpRPJLfJmTLZueJAmbgEtIMGl9lLKKH6YKy1AQd8lrsdJPPc7joZ6kCkEKlNLKhbUv",
+      "Program 11111111111111111111111111111111 success",
+      "Program 11111111111111111111111111111111 invoke [2]",
+      "Program 11111111111111111111111111111111 success",
+      "Program 11111111111111111111111111111111 invoke [2]",
+      "Program 11111111111111111111111111111111 success",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: Transfer",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2549 of 141128 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: CloseAccount",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1745 of 135127 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program log: UhUxVlc2hGeTBjNPCGmmZjvNSuBOYpfpRPJLfJmTLZueJAmbgEtIMGl9lLKKH6YKy1AQd8lrsdJPPc7joZ6kCkEKlNLKhbUv",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 consumed 73106 of 200000 compute units",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 success",
+    ];
+
+    const idl = {
+      version: "0.0.0",
+      name: "basic_1",
+      instructions: [
+        {
+          name: "initialize",
+          accounts: [],
+          args: [],
+        },
+      ],
+      events: [
+        {
+          name: "NftSold",
+          fields: [
+            {
+              name: "nftMintAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+            {
+              name: "accountAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+          ],
+        },
+      ],
+    };
+
+    const coder = new BorshCoder(idl);
+    const programId = new PublicKey(
+      "J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54"
+    );
+    const eventParser = new EventParser(programId, coder);
+
+    eventParser.parseLogs(logs, (event) => {
+      expect(event.name).toEqual("NftSold");
+      done();
+    });
+  });
+  it("Find event from logs", (done) => {
+    const logs = [
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 invoke [1]",
+      "Program log: Instruction: CancelListing",
+      "Program log: TRANSFERED SOME TOKENS",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: Transfer",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2549 of 182795 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program log: TRANSFERED SOME TOKENS",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: CloseAccount",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1745 of 176782 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program log: Vtv9xLjCsE60Ati9kl3VVU/5y8DMMeC4LaGdMLkX8WU+G59Wsi3wfky8rnO9otGb56CTRerWx3hB5M/SlRYBdht0fi+crAgFYsJcx2CHszpSWRkXNxYQ6DxQ/JqIvKnLC/8Mln7310A=",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 consumed 31435 of 200000 compute units",
+      "Program J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54 success",
+    ];
+
+    const idl = {
+      version: "0.0.0",
+      name: "basic_2",
+      instructions: [
+        {
+          name: "cancelListing",
+          accounts: [
+            {
+              name: "globalState",
+              isMut: true,
+              isSigner: false,
+            },
+            {
+              name: "nftHolderAccount",
+              isMut: true,
+              isSigner: false,
+            },
+            {
+              name: "listingAccount",
+              isMut: true,
+              isSigner: false,
+            },
+            {
+              name: "nftAssociatedAccount",
+              isMut: true,
+              isSigner: false,
+            },
+            {
+              name: "signer",
+              isMut: true,
+              isSigner: true,
+            },
+            {
+              name: "tokenProgram",
+              isMut: false,
+              isSigner: false,
+            },
+          ],
+          args: [],
+        },
+      ],
+      events: [
+        {
+          name: "ListingClosed",
+          fields: [
+            {
+              name: "initializer",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+            {
+              name: "nftMintAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+            {
+              name: "accountAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+          ],
+        },
+      ],
+    };
+
+    const coder = new BorshCoder(idl);
+    const programId = new PublicKey(
+      "J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54"
+    );
+    const eventParser = new EventParser(programId, coder);
+
+    eventParser.parseLogs(logs, (event) => {
+      expect(event.name).toEqual("ListingClosed");
+      done();
+    });
+  });
+  it("Listen to different program and send other program logs with same name", () => {
+    const logs = [
+      "Program 5VcVB7jEjdWJBkriXxayCrUUkwfhrPK3rXtnkxxUvMFP invoke [1]",
+      "Program log: Instruction: CancelListing",
+      "Program log: TRANSFERED SOME TOKENS",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: Transfer",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 2549 of 182795 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program log: TRANSFERED SOME TOKENS",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA invoke [2]",
+      "Program log: Instruction: CloseAccount",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA consumed 1745 of 176782 compute units",
+      "Program TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA success",
+      "Program log: Vtv9xLjCsE60Ati9kl3VVU/5y8DMMeC4LaGdMLkX8WU+G59Wsi3wfky8rnO9otGb56CTRerWx3hB5M/SlRYBdht0fi+crAgFYsJcx2CHszpSWRkXNxYQ6DxQ/JqIvKnLC/8Mln7310A=",
+      "Program 5VcVB7jEjdWJBkriXxayCrUUkwfhrPK3rXtnkxxUvMFP consumed 31435 of 200000 compute units",
+      "Program 5VcVB7jEjdWJBkriXxayCrUUkwfhrPK3rXtnkxxUvMFP success",
+    ];
+
+    const idl = {
+      version: "0.0.0",
+      name: "basic_2",
+      instructions: [],
+      events: [
+        {
+          name: "ListingClosed",
+          fields: [
+            {
+              name: "initializer",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+            {
+              name: "nftMintAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+            {
+              name: "accountAddress",
+              type: "publicKey" as "publicKey",
+              index: false,
+            },
+          ],
+        },
+      ],
+    };
+
+    const coder = new BorshCoder(idl);
+    const programId = new PublicKey(
+      "J2XMGdW2qQLx7rAdwWtSZpTXDgAQ988BLP9QTgUZvm54"
+    );
+    const eventParser = new EventParser(programId, coder);
+
     eventParser.parseLogs(logs, () => {
       throw new Error("Should never find logs");
     });
```

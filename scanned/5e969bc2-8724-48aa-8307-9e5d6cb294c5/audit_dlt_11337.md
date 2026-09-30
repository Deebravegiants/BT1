# [?] fix: prevent comptime println from crashing LSP (#5918)

## Summary
Severity: Unknown
Chain: ZK
Component: noir-lang/noir
Published: 2024-09-04
Source: https://github.com/noir-lang/noir/commit/44cf9a2140bc06b550d4b46966f1637598ac11a7
Type: security-commit

## Details
fix: prevent comptime println from crashing LSP (#5918)

# Description

## Problem

Resolves #5904

## Summary

I found out that writing to the error stream when connected to the LSP
client actually sends that output to the LSP output window ("Noir
Language Server") in our case so I chose to do that for comptime
println/print. Advantages:
- No more crashing of the LSP server on comptime println
- If you know it goes to that output you can actually see the output
without having to go to a terminal to run that code, so debugging
comptime will be pretty fast now
- (if you don't know the output goes there, it's fine too: at least the
LSP server doesn't crash 😄)


![lsp-comptime-println](https://github.com/user-attachments/assets/7d3ecaca-00fb-4c15-90a0-9868260ce7f5)

## Additional Context

Though the original issue was about using sockets to communicate with
the LSP client, I think we won't need that after all if comptime println
was the only issue (and I think most LSP servers use stdin/stdout for
communication because it's simpler).

Also: it would be better if this output showed up in a dedicated output
window, say "Noir Language comptime output" or something like that, but
only the LSP client can create those windows and write to them... so
implementing that would mean somehow communicating this data from the
server to the client (maybe a socket?), which is much harder to do... so
for now the output will have to show up like regular logs.

And a question: when the LSP server starts we have this code:

```rust
eprintln!("LSP starting...");
```

that shows up on the output window... should we remove it? It feel like
it was used to debug the server to know that it started, but I don't
know how useful it is now.

## Documentation

Check one:
- [x] No documentation needed.
- [ ] Documentation included in this PR.
- [ ] **[For Experimental Features]** Documentation to be submitted in a
separate PR.

# PR Checklist

- [x] I have tested the changes locally.
- [x] I have formatted the changes with [Prettier](https://prettier.io/)
and/or `cargo fmt` on default settings.

## Patch
### compiler/noirc_frontend/src/hir/comptime/interpreter.rs
```diff
@@ -1653,10 +1653,20 @@ impl<'local, 'interner> Interpreter<'local, 'interner> {
         assert_eq!(arguments.len(), 2);
 
         let print_newline = arguments[0].0 == Value::Bool(true);
-        if print_newline {
-            println!("{}", arguments[1].0.display(self.elaborator.interner));
+        let contents = arguments[1].0.display(self.elaborator.interner);
+        if self.elaborator.interner.is_in_lsp_mode() {
+            // If we `println!` in LSP it gets mixed with the protocol stream and leads to crashing
+            // the connection. If we use `eprintln!` not only it doesn't crash, but the output
+            // appears in the "Noir Language Server" output window in case you want to see it.
+            if print_newline {
+                eprintln!("{}", contents);
+            } else {
+                eprint!("{}", contents);
+            }
+        } else if print_newline {
+            println!("{}", contents);
         } else {
-            print!("{}", arguments[1].0.display(self.elaborator.interner));
+            print!("{}", contents);
         }
 
         Ok(Value::Unit)
```

### tooling/nargo_cli/src/cli/lsp_cmd.rs
```diff
@@ -35,8 +35,6 @@ pub(crate) fn run(_args: LspCommand, _config: NargoConfig) -> Result<(), CliErro
                 .service(router)
         });
 
-        eprintln!("LSP starting...");
-
         // Prefer truly asynchronous piped stdin/stdout without blocking tasks.
         #[cfg(unix)]
         let (stdin, stdout) = (
```

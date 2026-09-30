# [?] fix windows  stack overflow by using link-arg (#3445)

## Summary
Severity: Unknown
Chain: Starcoin
Component: starcoinorg/starcoin
Published: 2022-06-02
Source: https://github.com/starcoinorg/starcoin/commit/1c4190b922592ba7f244f08640e6933a80baccfe
Type: security-commit

## Details
fix windows  stack overflow by using link-arg (#3445)

## Patch
### .cargo/config
```diff
@@ -12,7 +12,7 @@ retry = 2
 git-fetch-with-cli = true
 
 [target.x86_64-pc-windows-msvc]
-rustflags = ["-C", "link-arg=-fuse-ld=lld"]
+rustflags = ["-C", "link-arg=/STACK:8000000"]
 
 # ========== EXPERIMENTAL MOLD LINKER SUPPORT ==========
 # [target.x86_64-unknown-linux-gnu]
```

### vm/stdlib/.cargo/config.toml
```diff
@@ -0,0 +1,2 @@
+[target.x86_64-pc-windows-msvc]
+rustflags = ["-C", "link-arg=/STACK:8000000"]
```

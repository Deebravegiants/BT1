# [?] fix: `cargo-chef` panic issue (#98)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2022-11-16
Source: https://github.com/scroll-tech/scroll/commit/00f3a6fed6fc97b9320159bd4e53365a62e46ff0
Type: security-commit

## Details
fix: `cargo-chef` panic issue (#98)

Co-authored-by: Steven Gu <steven.gu@crypto.com>

## Patch
### build/dockerfiles/intermediate/go-rust-builder.Dockerfile
```diff
@@ -6,7 +6,8 @@ RUN apk add --no-cache gcc musl-dev linux-headers git ca-certificates
 
 ENV RUSTUP_HOME=/usr/local/rustup \
     CARGO_HOME=/usr/local/cargo \
-    PATH=/usr/local/cargo/bin:$PATH
+    PATH=/usr/local/cargo/bin:$PATH \
+    CARGO_NET_GIT_FETCH_WITH_CLI=true
 
 RUN set -eux; \
     apkArch="$(apk --print-arch)"; \
```

### build/dockerfiles/intermediate/rust-alpine-builder.Dockerfile
```diff
@@ -6,11 +6,13 @@ ARG DEFAULT_RUST_TOOLCHAIN=nightly-2022-08-23
 RUN apk add --no-cache \
         ca-certificates \
         gcc \
+        git \
         musl-dev
 
 ENV RUSTUP_HOME=/usr/local/rustup \
     CARGO_HOME=/usr/local/cargo \
-    PATH=/usr/local/cargo/bin:$PATH
+    PATH=/usr/local/cargo/bin:$PATH \
+    CARGO_NET_GIT_FETCH_WITH_CLI=true
 
 RUN set -eux; \
     apkArch="$(apk --print-arch)"; \
```

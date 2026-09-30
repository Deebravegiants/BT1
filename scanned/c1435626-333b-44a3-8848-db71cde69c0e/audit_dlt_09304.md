# [?] fix: forge doc panic (#10901)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2025-07-02
Source: https://github.com/foundry-rs/foundry/commit/6983a938580a1eb25d9dbd61eb8cad8cd137a86d
Type: security-commit

## Details
fix: forge doc panic (#10901)

fix forge doc panic

## Patch
### crates/forge/src/cmd/doc/server.rs
```diff
@@ -94,7 +94,7 @@ impl Server {
 async fn serve(build_dir: PathBuf, address: SocketAddr, file_404: &str) -> io::Result<()> {
     let file_404 = build_dir.join(file_404);
     let svc = ServeDir::new(build_dir).not_found_service(ServeFile::new(file_404));
-    let app = Router::new().nest_service("/", get_service(svc));
+    let app = Router::new().fallback_service(get_service(svc));
     let tcp_listener = tokio::net::TcpListener::bind(address).await?;
     axum::serve(tcp_listener, app.into_make_service()).await
 }
```

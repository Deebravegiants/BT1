# [M] actix-files has a possible exposure of information vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8v2v-wjwg-vx6r
CWE: CWE-200
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-8v2v-wjwg-vx6r
Type: github-advisory

## Affected
- crates.io: `actix-files` — affected >=0 <0.6.10

## Details
### Summary

When passing a non-existing folder to the `actix_files::Files::new()` method causes the actix server to expose unexpected files.

### Details

The `actix-files` library exposes a [`Files` struct](https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L38) that configures an actix `service` to serve the files in a folder as static assets. Below you can find the [signature of the `Files::new` method](https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L98):

```rust
pub fn new<T: Into<PathBuf>>(mount_path: &str, serve_from: T) -> Files
```

When the `mount_path` you pass to `Files` doesn't exist, [it defaults to an empty path](https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L104) (`Path::new()`). When the service receives a HTTP request, it [joins the request information with the empty path](https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/service.rs#L136) and calls `canonicalize`. Rust resolves this path as relative and returns any file that matches it.

This behavior causes the library to expose unexpected files when the folder is not present.

### PoC

_There is a working PoC on https://github.com/Angelmmiguel/actix-files-vuln, although the next steps can be followed to reproduce the issue_

1. Clone the https://github.com/actix/examples repository.
2. Change your directory to the `basics/static-files` folder.
3. Edit the `src/main.rs` file and change the line 13 to mount a non-existing folder:

    ```diff
    -        .service(Files::new("/images", "static/images/").show_files_listing())
    +        .service(Files::new("/images", "static/missing/").show_files_listing())
    ```
    
4. Run the project with `cargo run`.
5. Access the <http://localhost:8080/images/Cargo.toml> URL.

### Impact

This is an exposure of information vulnerability. It affects anyone using the `actix-files::Files` library that mounts a non-existing folder for any reason.

## References
- https://github.com/actix/actix-web/security/advisories/GHSA-8v2v-wjwg-vx6r
- https://github.com/actix/actix-web
- https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L104
- https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L38
- https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/files.rs#L98
- https://github.com/actix/actix-web/blob/fba766b4beb92278665d58815c94d336015225c5/actix-files/src/service.rs#L136

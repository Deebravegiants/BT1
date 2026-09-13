# [M] RustEmbed generated `get` method allows for directory traversal when reading files from disk

## Summary
Severity: Medium
Advisory: GHSA-cgw6-f3mj-h742
CWE: CWE-22
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-cgw6-f3mj-h742
Type: github-advisory

## Affected
- crates.io: `rust-embed` — affected >=0 <6.3.0

## Details
When running in debug mode and the `debug-embed` (off by default) feature is
not enabled, the generated `get` method does not check that the input path is
a child of the folder given. 

This allows attackers to read arbitrary files in the file system if they have
control over the filename given. The following code will print the contents of
your `/etc/passwd` if adjusted with a correct number of `../`s depending on
where it is run from.

```rust
#[derive(rust_embed::RustEmbed)]
#[folder = "src/"]
pub struct Asset;

fn main() {
    let d = Asset::get("../../../etc/passwd").unwrap().data;
    println!("{}", String::from_utf8_lossy(&d));
}
```

The flaw was corrected by canonicalizing the input filename and ensuring that
it starts with the canonicalized folder path.

## References
- https://github.com/pyros2097/rust-embed/issues/159
- https://github.com/pyros2097/rust-embed
- https://rustsec.org/advisories/RUSTSEC-2021-0126.html

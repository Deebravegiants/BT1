# [H] Arbitrary file overwrite in tar-rs

## Summary
Severity: High
Advisory: GHSA-2367-c296-3mp2
CVE: CVE-2018-20990
CWE: CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2367-c296-3mp2
Type: github-advisory

## Affected
- crates.io: `tar` — affected >=0 <0.4.16

## Details
When unpacking a tarball with the unpack_in-family of functions it's intended that only files within the specified directory are able to be written. Tarballs with hard links or symlinks, however, can be used to overwrite any file on the filesystem. Tarballs can contain multiple entries for the same file. A tarball which first contains an entry for a hard link or symlink pointing to any file on the filesystem will have the link created, and then afterwards if the same file is listed in the tarball the hard link will be rewritten and any file can be rewritten on the filesystem.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-20990
- https://github.com/alexcrichton/tar-rs/pull/156
- https://github.com/alexcrichton/tar-rs/commit/54651a87ae6ba7d81fcc72ffdee2ea7eca2c7e85
- https://github.com/alexcrichton/tar-rs
- https://rustsec.org/advisories/RUSTSEC-2018-0002.html

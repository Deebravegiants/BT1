# [M] Tauri Filesystem Scope Glob Pattern is too Permissive

## Summary
Severity: Medium
Advisory: GHSA-6mv3-wm7j-h4w5
CVE: CVE-2022-46171
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-22
Source: https://github.com/advisories/GHSA-6mv3-wm7j-h4w5
Type: github-advisory

## Affected
- crates.io: `tauri` — affected >=1.0.0 <1.0.8
- crates.io: `tauri` — affected >=1.1.0 <1.1.3
- crates.io: `tauri` — affected >=1.2.0 <1.2.3
- crates.io: `tauri` — affected >=2.0.0-alpha.0 <2.0.0-alpha.2

## Details
### Impact

The filesystem glob pattern wildcards `*`, `?`, and `[...]` match file path literals and leading dots by default, which unintentionally exposes sub folder content of allowed paths.

Example: The `fs` scope `$HOME/*.key` would also allow `$HOME/.ssh/secret.key` to be read even though it is in a sub directory of `$HOME` and is inside a hidden folder.

Scopes without the wildcards are not affected. As `**` allows for sub directories the behavior there is also as expected.

### Patches

The issue has been patched in the latest release and was backported into the currently supported 1.x branches.

### Workarounds

No workaround is known at the time of publication.

### References

The original report contained information that the `dialog.open` component automatically allows one sub directory to be read, regardless of the `recursive` option.

Imagine a file system looking like
```
 o ../
 o documents/
    - file.txt
    - deeper/
       o deep_file.txt
```

Reproduction steps:

1. Trying to load “file.txt” or “deep_file.txt” doesn’t work. Expected
2. Select “documents” as folder to open(ie. with window.__TAURI__.dialog.open)
3. Trying to load “file.txt” works. Expected
5. Trying to load “deep_file.txt” also works, which isn’t expected

The recursive flag is used in https://github.com/tauri-apps/tauri/blob/cd8c074ae6592303d3f6844a4fb6d262eae913b2/core/tauri/src/scope/fs.rs#L154 to scope the filesystem access to either files in the folder or to also include sub directories.

The original issue was replicated and further investigated.

The root cause was triaged to the `glob` crate facilitating defaults, which allow the `*` and `[...]` to also match path literals.

```rust
MatchOptions {
    case_sensitive: true,
    require_literal_separator: false,
    require_literal_leading_dot: false
}
```

This implicated that not only the `dialog.open` component was affected but rather all `fs` scopes containing the `*` or `[...]` glob.
During this investigation it became obvious that the current glob matches would also match hidden folder (e.g: `.ssh`) content by default, without explicitly allowing hidden folders to be matched. This is not commonly expected behavior in comparison to for example `bash`.

The new default  Match options are:

```rust
MatchOptions {
    case_sensitive: true,
    require_literal_separator: true,
    require_literal_leading_dot: true
}
```

> Another note security relevant for developers building applications interacting with case sensitive filesystems is, that the `case_sensitive` option only affects ASCII file paths and is not valid in Unicode based paths. This is considered a known risk until the `glob` crate supports non-ASCII file paths for this type of case sensitive matching.

### For more Information

If you have any questions or comments about this advisory:

Open an issue in tauri
Email us at [security@tauri.app](mailto:security@tauri.app)

## References
- https://github.com/tauri-apps/tauri/security/advisories/GHSA-6mv3-wm7j-h4w5
- https://nvd.nist.gov/vuln/detail/CVE-2022-46171
- https://github.com/tauri-apps/tauri/commit/14d567f7ecb25a6d1024cf3d796f86aee89d0dd4
- https://github.com/tauri-apps/tauri/commit/72389b00d7b495ffd7750eb1e75a3b8537d07cf3
- https://github.com/tauri-apps/tauri/commit/f0602e7c294245ab6ef6fbf2a976ef398340ef58
- https://github.com/tauri-apps/tauri

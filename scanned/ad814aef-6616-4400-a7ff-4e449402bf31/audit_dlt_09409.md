# [?] Merge pull request #2898 from tnull/2024-02-ignore-RUSTSEC-2021-0145

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-02-20
Source: https://github.com/lightningdevkit/rust-lightning/commit/a854ccb9b5dfa762ae22e2e547630eb3f8e4235b
Type: security-commit

## Details
Merge pull request #2898 from tnull/2024-02-ignore-RUSTSEC-2021-0145

Have CI's `cargo audit` ignore `RUSTSEC-2021-0125`

## Patch
### .github/workflows/audit.yml
```diff
@@ -15,3 +15,9 @@ jobs:
       - uses: rustsec/audit-check@v1.4.1
         with:
           token: ${{ secrets.GITHUB_TOKEN }}
+          ignore: "RUSTSEC-2021-0145"
+              # RUSTSEC-2021-0145 pertains `atty`, which is a depencency of
+              # `criterion`. While the latter removed the depencency in its
+              # newest version, it would also require a higher `rustc`. We
+              # therefore avoid bumping it to allow benchmarking with our
+              # `rustc` 1.63 MSRV.
```

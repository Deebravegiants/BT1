# [?] Have CI's `cargo audit` ignore `RUSTSEC-2021-0125`

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningdevkit/rust-lightning
Published: 2024-02-16
Source: https://github.com/lightningdevkit/rust-lightning/commit/9aa6ddb24e3063787595a1ef06a84afac23f15c6
Type: security-commit

## Details
Have CI's `cargo audit` ignore `RUSTSEC-2021-0125`

This advisory is only relevant for a downstream dependency of
`criterion`, which we currently don't want to bump in order to continue
benchmarking with our MSRV 1.63.0.

We therefore just add it to our ignore list for now.

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

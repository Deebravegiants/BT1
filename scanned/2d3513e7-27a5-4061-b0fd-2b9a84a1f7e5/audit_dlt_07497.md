# [?] fix(audit): ignore `RUSTSEC-2023-0071`

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2024-07-15
Source: https://github.com/fedimint/fedimint/commit/31f9601a22dc76eb9c67009163e50b35a36301be
Type: security-commit

## Details
fix(audit): ignore `RUSTSEC-2023-0071`

Add `RUSTSEC-2023-0071` to ignored advisories list on `audit.toml`, it's
added to ignore because it currently doesn't have a fix and it's a
transitive dependency from `arti_client` and tor ecosystem.

In `arti` project it has also been ignored, and the team mentioned it's
not currently impacted as it does not do any private key operation with
RSA. Please check: https://gitlab.torproject.org/tpo/core/arti/-/issues/1141

`RUSTSEC-2023-0071`: https://rustsec.org/advisories/RUSTSEC-2023-0071

## Patch
### .cargo/audit.toml
```diff
@@ -9,4 +9,4 @@
 #
 # See the full example in: https://raw.githubusercontent.com/rustsec/rustsec/main/cargo-audit/audit.toml.example
 [advisories]
-ignore = ["RUSTSEC-2023-0052"] 
+ignore = ["RUSTSEC-2023-0052", "RUSTSEC-2023-0071"]
```

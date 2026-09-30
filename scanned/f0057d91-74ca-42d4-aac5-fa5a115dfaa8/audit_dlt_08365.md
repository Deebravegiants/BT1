# [?] [ci] add RUSTSEC-2020-0146 to nightly ignore list

## Summary
Severity: Unknown
Chain: Move
Component: move-language/move
Published: 2021-03-22
Source: https://github.com/move-language/move/commit/6eefd5785f1633f058fea5b006d9ed7632ca0564
Type: security-commit

## Details
[ci] add RUSTSEC-2020-0146 to nightly ignore list

The vulnerable version of generic-array is a transitive dep.

Closes: #8011

## Patch
### .github/workflows/daily.yml
```diff
@@ -30,8 +30,9 @@ jobs:
       - name: audit crates
         # List of ignored RUSTSEC
         # 1. RUSTSEC-2021-0020 - Not impacted, see #7723
+        # 2. RUSTSEC-2020-0146 - Not impacted, see #7826
         run: |
-          $CARGO $CARGOFLAGS audit --ignore RUSTSEC-2021-0020 >> $MESSAGE_PAYLOAD_FILE
+          $CARGO $CARGOFLAGS audit --ignore RUSTSEC-2021-0020 --ignore RUSTSEC-2020-0146 >> $MESSAGE_PAYLOAD_FILE
       - uses: ./.github/actions/slack-file
         with:
           webhook: ${{ secrets.WEBHOOK_AUDIT }}
```

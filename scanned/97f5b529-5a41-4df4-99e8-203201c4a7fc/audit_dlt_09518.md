# [?] add RUSTSEC-2023-0063 to config.toml (#4040)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2023-09-21
Source: https://github.com/chainflip-io/chainflip-backend/commit/e94f1f2921728e5af8357d153bc88cfb96d40f46
Type: security-commit

## Details
add RUSTSEC-2023-0063 to config.toml (#4040)

## Patch
### .cargo/config.toml
```diff
@@ -36,6 +36,7 @@ tree --no-default-features --depth 1 --edges=features,normal
 # - RUSTSEC-2023-0053: This advisory comes from rustls-webpki, a dependency of ethers-rs. CPU denial of service in certificate path building.
 # - RUSTSEC-2021-0060: This is a transitive dependency of libp2p and will be fixed in an upcoming release.
 # - RUSTSEC-2021-0059: This is a transitive dependency of libp2p and will be fixed in an upcoming release.
+# - RUSTSEC-2023-0063: This is a transitive dependency of libp2p and it is not used.
 cf-audit = '''
 audit --ignore RUSTSEC-2022-0061
       --ignore RUSTSEC-2020-0071
@@ -47,4 +48,5 @@ audit --ignore RUSTSEC-2022-0061
       --ignore RUSTSEC-2023-0053
       --ignore RUSTSEC-2021-0060
       --ignore RUSTSEC-2021-0059
+      --ignore RUSTSEC-2023-0063
 '''
```

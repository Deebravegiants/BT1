# [?] Fix Vulnerability issue in read-the-docs-site (#5430)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2023-07-21
Source: https://github.com/IntersectMBO/plutus/commit/4c6e0c9ece573eeced88619f814791b1ebfaeefb
Type: security-commit

## Details
Fix Vulnerability issue in read-the-docs-site (#5430)

## Patch
### doc/read-the-docs-site/requirements.txt
```diff
@@ -29,7 +29,7 @@ ptyprocess==0.7.0
 pybtex==0.24.0
 pybtex-docutils==1.0.1
 pycparser==2.21
-Pygments==2.11.2
+Pygments==2.15.0
 pyparsing==3.0.6
 PySocks==1.7.1
 PyStemmer==2.0.1
```

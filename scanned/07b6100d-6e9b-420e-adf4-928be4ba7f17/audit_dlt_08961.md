# [?] CVE-2025-27516 - updated jinja2 to 3.1.6 (#5271)

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2025-08-18
Source: https://github.com/hyperledger/fabric/commit/588393944da41ea7d393691cdd542024918c3e85
Type: security-commit

## Details
CVE-2025-27516 - updated jinja2 to 3.1.6 (#5271)

Signed-off-by: Ketul Shah <shah.ketul@ibm.com>

## Patch
### docs/requirements.txt
```diff
@@ -7,7 +7,7 @@ docutils==0.21.2
 idna==3.10
 imagesize==1.4.1
 importlib-metadata==8.5.0
-Jinja2==3.1.5
+Jinja2==3.1.6
 markdown-it-py==3.0.0
 MarkupSafe==3.0.1
 mdit-py-plugins==0.4.2
```

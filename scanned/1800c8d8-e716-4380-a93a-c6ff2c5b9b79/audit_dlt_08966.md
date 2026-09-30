# [?] Upgrade the CouchDB used to v3.3.3 as per CVE-2023-45725.

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2024-01-05
Source: https://github.com/hyperledger/fabric/commit/844e281c2d11b79c4330ba3b4231267af9efebb2
Type: security-commit

## Details
Upgrade the CouchDB used to v3.3.3 as per CVE-2023-45725.

Tracked by https://github.com/hyperledger/fabric/issues/4594

Signed-off-by: Ben Smith <benjsmi@us.ibm.com>

## Patch
### Makefile
```diff
@@ -51,7 +51,7 @@ FABRIC_VER ?= 3.0.0
 
 # 3rd party image version
 # These versions are also set in the runners in ./integration/runners/
-COUCHDB_VER ?= 3.3.2
+COUCHDB_VER ?= 3.3.3
 
 # Disable implicit rules
 .SUFFIXES:
```

### integration/nwo/runner/couchdb.go
```diff
@@ -24,7 +24,7 @@ import (
 )
 
 const (
-	CouchDBDefaultImage = "couchdb:3.3.2"
+	CouchDBDefaultImage = "couchdb:3.3.3"
 	CouchDBUsername     = "admin"
 	CouchDBPassword     = "adminpw"
 )
```

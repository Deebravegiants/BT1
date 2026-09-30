# [?] try to fix deadlock/timeout in logpoller tests (#22337)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2026-05-08
Source: https://github.com/smartcontractkit/chainlink/commit/70dbd23bbbb7c38ee82a32bdf285f35589d25f70
Type: security-commit

## Details
try to fix deadlock/timeout in logpoller tests (#22337)

bump chainlink-evm dep to a version with fixed test deadlock

## Patch
### core/scripts/go.mod
```diff
@@ -49,7 +49,7 @@ require (
 	github.com/smartcontractkit/chainlink-common/keystore v1.1.0
 	github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91
 	github.com/smartcontractkit/chainlink-deployments-framework v0.100.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20260505131349-78e491b80735
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.18.0
```

### core/scripts/go.sum
```diff
@@ -1651,8 +1651,8 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aa
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91/go.mod h1:Fl6b/I5qn5TcEh85FP1rNsJ7stcYtmXhVbM2W5RuzQg=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0 h1:M8+wVsfqgcxzH5WP9NEK5FFlEgU1r+6kD3ow0kURx7E=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0/go.mod h1:yWSgE8ZqcY9vERwBkDRARBbUfFFEyzICOg4Gqi9Yrng=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1 h1:qcP91lWASRAJ7JgzdvMmF/BMb5m1dwvAq8PGCIcqrWM=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d h1:+zUmapuseG/BWHmBoM3Cl7LEr2frKr59q+eVKgBV9Zk=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501 h1:QJiXTG9CmaQAuMRn5JGi+Jhji7fSkehVnKpjc8oNJJY=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501/go.mod h1:4cT1BeNF8DAn6In9zr3LayVCv1KzFeuxT7zcuNkfIb0=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828 h1:BmsFk/TSHL6dPPR86GTqgSrUXLSINNFC6cfpFRrQX+4=
```

### deployment/go.mod
```diff
@@ -45,7 +45,7 @@ require (
 	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260506120607-7f10be016c89
 	github.com/smartcontractkit/chainlink-common/keystore v1.1.0
 	github.com/smartcontractkit/chainlink-deployments-framework v0.100.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20260505131349-78e491b80735
```

### deployment/go.sum
```diff
@@ -1394,8 +1394,8 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aa
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91/go.mod h1:Fl6b/I5qn5TcEh85FP1rNsJ7stcYtmXhVbM2W5RuzQg=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0 h1:M8+wVsfqgcxzH5WP9NEK5FFlEgU1r+6kD3ow0kURx7E=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0/go.mod h1:yWSgE8ZqcY9vERwBkDRARBbUfFFEyzICOg4Gqi9Yrng=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1 h1:qcP91lWASRAJ7JgzdvMmF/BMb5m1dwvAq8PGCIcqrWM=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d h1:+zUmapuseG/BWHmBoM3Cl7LEr2frKr59q+eVKgBV9Zk=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501 h1:QJiXTG9CmaQAuMRn5JGi+Jhji7fSkehVnKpjc8oNJJY=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501/go.mod h1:4cT1BeNF8DAn6In9zr3LayVCv1KzFeuxT7zcuNkfIb0=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828 h1:BmsFk/TSHL6dPPR86GTqgSrUXLSINNFC6cfpFRrQX+4=
```

### docs/CONFIG.md
```diff
@@ -10127,8 +10127,8 @@ Mode = 'BlockHistory'
 PriceDefault = '20 gwei'
 PriceMax = '120 gwei'
 PriceMin = '1 gwei'
-LimitDefault = 80000000000
-LimitMax = 100000000000
+LimitDefault = 500000
+LimitMax = 500000
 LimitMultiplier = '1'
 LimitTransfer = 21000
 EstimateLimit = false
@@ -10252,8 +10252,8 @@ Mode = 'BlockHistory'
 PriceDefault = '20 gwei'
 PriceMax = '120 gwei'
 PriceMin = '1 gwei'
-LimitDefault = 80000000000
-LimitMax = 100000000000
+LimitDefault = 500000
+LimitMax = 500000
 LimitMultiplier = '1'
 LimitTransfer = 21000
 EstimateLimit = false
```

### go.mod
```diff
@@ -89,7 +89,7 @@ require (
 	github.com/smartcontractkit/chainlink-common/keystore v1.1.0
 	github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.10
 	github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260119171452-39c98c3b33cd
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135
```

### go.sum
```diff
@@ -1190,8 +1190,8 @@ github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.10 h1:FJAFgXS9
 github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.10/go.mod h1:oiDa54M0FwxevWwyAX773lwdWvFYYlYHHQV1LQ5HpWY=
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91 h1:s8E4EYRKEjghJFDnIWQxw8zoCvORVolIY/EKZ+JmzRc=
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91/go.mod h1:Fl6b/I5qn5TcEh85FP1rNsJ7stcYtmXhVbM2W5RuzQg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1 h1:qcP91lWASRAJ7JgzdvMmF/BMb5m1dwvAq8PGCIcqrWM=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d h1:+zUmapuseG/BWHmBoM3Cl7LEr2frKr59q+eVKgBV9Zk=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501 h1:QJiXTG9CmaQAuMRn5JGi+Jhji7fSkehVnKpjc8oNJJY=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501/go.mod h1:4cT1BeNF8DAn6In9zr3LayVCv1KzFeuxT7zcuNkfIb0=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260119171452-39c98c3b33cd h1:sK+pK4epQp20yQ7XztwrVgkTkRAr4FY+TvEegW8RuQk=
```

### integration-tests/go.mod
```diff
@@ -32,7 +32,7 @@ require (
 	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260506120607-7f10be016c89
 	github.com/smartcontractkit/chainlink-common/keystore v1.1.0
 	github.com/smartcontractkit/chainlink-deployments-framework v0.100.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.18.0
 	github.com/smartcontractkit/chainlink-sui v0.0.0-20260429183453-39df0198aed8
```

### integration-tests/go.sum
```diff
@@ -1379,8 +1379,8 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aa
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91/go.mod h1:Fl6b/I5qn5TcEh85FP1rNsJ7stcYtmXhVbM2W5RuzQg=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0 h1:M8+wVsfqgcxzH5WP9NEK5FFlEgU1r+6kD3ow0kURx7E=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0/go.mod h1:yWSgE8ZqcY9vERwBkDRARBbUfFFEyzICOg4Gqi9Yrng=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1 h1:qcP91lWASRAJ7JgzdvMmF/BMb5m1dwvAq8PGCIcqrWM=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d h1:+zUmapuseG/BWHmBoM3Cl7LEr2frKr59q+eVKgBV9Zk=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501 h1:QJiXTG9CmaQAuMRn5JGi+Jhji7fSkehVnKpjc8oNJJY=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501/go.mod h1:4cT1BeNF8DAn6In9zr3LayVCv1KzFeuxT7zcuNkfIb0=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828 h1:BmsFk/TSHL6dPPR86GTqgSrUXLSINNFC6cfpFRrQX+4=
```

### integration-tests/load/go.mod
```diff
@@ -22,7 +22,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20260415165642-49f23e4d76cc
 	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260506120607-7f10be016c89
 	github.com/smartcontractkit/chainlink-deployments-framework v0.100.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-testing-framework/framework v0.15.19
 	github.com/smartcontractkit/chainlink-testing-framework/havoc v1.50.5
 	github.com/smartcontractkit/chainlink-testing-framework/seth v1.51.5
```

### integration-tests/load/go.sum
```diff
@@ -1649,8 +1649,8 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aa
 github.com/smartcontractkit/chainlink-data-streams v0.1.14-0.20260504075031-e5aae8c82e91/go.mod h1:Fl6b/I5qn5TcEh85FP1rNsJ7stcYtmXhVbM2W5RuzQg=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0 h1:M8+wVsfqgcxzH5WP9NEK5FFlEgU1r+6kD3ow0kURx7E=
 github.com/smartcontractkit/chainlink-deployments-framework v0.100.0/go.mod h1:yWSgE8ZqcY9vERwBkDRARBbUfFFEyzICOg4Gqi9Yrng=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1 h1:qcP91lWASRAJ7JgzdvMmF/BMb5m1dwvAq8PGCIcqrWM=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d h1:+zUmapuseG/BWHmBoM3Cl7LEr2frKr59q+eVKgBV9Zk=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d/go.mod h1:6EpqRtmiA3smgCRNVSN/IorekINrftZPX5QhoNrCaj4=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501 h1:QJiXTG9CmaQAuMRn5JGi+Jhji7fSkehVnKpjc8oNJJY=
 github.com/smartcontractkit/chainlink-evm/contracts/cre/gobindings v0.0.0-20260403151002-2c91155b5501/go.mod h1:4cT1BeNF8DAn6In9zr3LayVCv1KzFeuxT7zcuNkfIb0=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828 h1:BmsFk/TSHL6dPPR86GTqgSrUXLSINNFC6cfpFRrQX+4=
```

### system-tests/lib/go.mod
```diff
@@ -36,7 +36,7 @@ require (
 	github.com/smartcontractkit/chainlink-common v0.11.2-0.20260506120607-7f10be016c89
 	github.com/smartcontractkit/chainlink-common/keystore v1.1.0
 	github.com/smartcontractkit/chainlink-deployments-framework v0.100.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260506131038-e5dfcb4456a1
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20260507171202-46e6a397da2d
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20260421142741-9c7fbaf7c828
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20260505131349-78e491b80735
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.18.0
```

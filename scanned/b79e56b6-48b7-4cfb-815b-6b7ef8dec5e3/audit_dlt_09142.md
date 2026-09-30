# [?] Fix Solana LogPoller panic (#18338)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-06-25
Source: https://github.com/smartcontractkit/chainlink/commit/4468c8e01b2d0078047e50ea91400d5e9ce7bc45
Type: security-commit

## Details
Fix Solana LogPoller panic (#18338)

* Bumped chainlink-solana dependency

* Updated plugins

## Patch
### core/scripts/go.mod
```diff
@@ -405,7 +405,7 @@ require (
 	github.com/smartcontractkit/chainlink-protos/rmn/v1.6/go v0.0.0-20250131130834-15e0d4cde2a6 // indirect
 	github.com/smartcontractkit/chainlink-protos/svr v1.1.0 // indirect
 	github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c // indirect
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 // indirect
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/parrot v0.6.2 // indirect
 	github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df // indirect
 	github.com/smartcontractkit/freeport v0.1.1 // indirect
```

### core/scripts/go.sum
```diff
@@ -1319,8 +1319,8 @@ github.com/smartcontractkit/chainlink-protos/svr v1.1.0 h1:79Z9N9dMbMVRGaLoDPAQ+
 github.com/smartcontractkit/chainlink-protos/svr v1.1.0/go.mod h1:TcOliTQU6r59DwG4lo3U+mFM9WWyBHGuFkkxQpvSujo=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c h1:o+f69x7YeWAAW3UV1c+T2jSRr0nB8tNyZEEbufDMNi4=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c/go.mod h1:HIpGvF6nKCdtZ30xhdkKWGM9+4Z4CVqJH8ZBL1FTEiY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 h1:NK8TluG1JtjUt+g9HlyFtlJkfysTc2fhuxGA9NiZKwY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9/go.mod h1:kYEark+msACtYT027qNRx1NoQCCy94WNMSQxmUKOLWI=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 h1:osscyk2QY5FZjfd6lDbQu4fkovmoCSB4gOrF7AoCrEY=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3/go.mod h1:gCfn7vgwB6CB9KNVZtRCwfmgUY9MY79sgKJry+dfkZ4=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.3 h1:jey+Y64hAo/lljBLDQ9K5hwajUL7xd8onjXOebCEj+A=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.3/go.mod h1:q99H9vcMJDs6T+zsSI8XJZd6PUkZnyG3iaRbrYNUCTk=
 github.com/smartcontractkit/chainlink-testing-framework/lib v1.54.3 h1:4Bned1rumiWB7A0WI4hcEVuOnBBHIoXpxagZYhPLFNw=
```

### deployment/go.mod
```diff
@@ -41,7 +41,7 @@ require (
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20250522110034-65c54665034a
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.12.0
 	github.com/smartcontractkit/chainlink-protos/orchestrator v0.7.0
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3
 	github.com/smartcontractkit/chainlink-testing-framework/lib v1.52.4
 	github.com/smartcontractkit/freeport v0.1.1
 	github.com/smartcontractkit/libocr v0.0.0-20250604151357-2fe8c61bbf2e
```

### deployment/go.sum
```diff
@@ -1295,8 +1295,8 @@ github.com/smartcontractkit/chainlink-protos/svr v1.1.0 h1:79Z9N9dMbMVRGaLoDPAQ+
 github.com/smartcontractkit/chainlink-protos/svr v1.1.0/go.mod h1:TcOliTQU6r59DwG4lo3U+mFM9WWyBHGuFkkxQpvSujo=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c h1:o+f69x7YeWAAW3UV1c+T2jSRr0nB8tNyZEEbufDMNi4=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c/go.mod h1:HIpGvF6nKCdtZ30xhdkKWGM9+4Z4CVqJH8ZBL1FTEiY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 h1:NK8TluG1JtjUt+g9HlyFtlJkfysTc2fhuxGA9NiZKwY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9/go.mod h1:kYEark+msACtYT027qNRx1NoQCCy94WNMSQxmUKOLWI=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 h1:osscyk2QY5FZjfd6lDbQu4fkovmoCSB4gOrF7AoCrEY=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3/go.mod h1:gCfn7vgwB6CB9KNVZtRCwfmgUY9MY79sgKJry+dfkZ4=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0 h1:jdftGHqULouQ1bTc92C+PDF6reypEWwdbvG//5yYI0U=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0/go.mod h1:q99H9vcMJDs6T+zsSI8XJZd6PUkZnyG3iaRbrYNUCTk=
 github.com/smartcontractkit/chainlink-testing-framework/lib v1.52.4 h1:+kwLuO9kcq1+ZbRUQjxX1SQmzlL2M6ZP6+L0xQMtmkU=
```

### go.mod
```diff
@@ -89,7 +89,7 @@ require (
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20250612182447-1c32d2efe48f
 	github.com/smartcontractkit/chainlink-protos/orchestrator v0.7.0
 	github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250611193111-99542a0c5d58
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3
 	github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df
 	github.com/smartcontractkit/freeport v0.1.1
 	github.com/smartcontractkit/libocr v0.0.0-20250604151357-2fe8c61bbf2e
```

### go.sum
```diff
@@ -1112,8 +1112,8 @@ github.com/smartcontractkit/chainlink-protos/svr v1.1.0 h1:79Z9N9dMbMVRGaLoDPAQ+
 github.com/smartcontractkit/chainlink-protos/svr v1.1.0/go.mod h1:TcOliTQU6r59DwG4lo3U+mFM9WWyBHGuFkkxQpvSujo=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c h1:o+f69x7YeWAAW3UV1c+T2jSRr0nB8tNyZEEbufDMNi4=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c/go.mod h1:HIpGvF6nKCdtZ30xhdkKWGM9+4Z4CVqJH8ZBL1FTEiY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250611193111-99542a0c5d58 h1:JSfI0YDNtSTPbv6zoATtDwPaV+hIuhvZiViZOKsounM=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250611193111-99542a0c5d58/go.mod h1:kYEark+msACtYT027qNRx1NoQCCy94WNMSQxmUKOLWI=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 h1:osscyk2QY5FZjfd6lDbQu4fkovmoCSB4gOrF7AoCrEY=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3/go.mod h1:gCfn7vgwB6CB9KNVZtRCwfmgUY9MY79sgKJry+dfkZ4=
 github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df h1:Fu9FHmpkcA0S75bO3heYRkYXpOfxpIv6yI/OQRjOhL8=
 github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df/go.mod h1:EQl7VcrSvpSNOL8qWkc2CV/2cOII5CIkKTeIqzqCWKk=
 github.com/smartcontractkit/chainlink-tron/relayer/gotron-sdk v0.0.5-0.20250528121202-292529af39df h1:36e3ROIZyV/qE8SvFOACXtXfMOMd9vG4+zY2v2ScXkI=
```

### integration-tests/go.mod
```diff
@@ -468,7 +468,7 @@ require (
 	github.com/smartcontractkit/chainlink-protos/rmn/v1.6/go v0.0.0-20250131130834-15e0d4cde2a6 // indirect
 	github.com/smartcontractkit/chainlink-protos/svr v1.1.0 // indirect
 	github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c // indirect
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 // indirect
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0 // indirect
 	github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df // indirect
 	github.com/smartcontractkit/freeport v0.1.1 // indirect
```

### integration-tests/go.sum
```diff
@@ -1516,8 +1516,8 @@ github.com/smartcontractkit/chainlink-protos/svr v1.1.0 h1:79Z9N9dMbMVRGaLoDPAQ+
 github.com/smartcontractkit/chainlink-protos/svr v1.1.0/go.mod h1:TcOliTQU6r59DwG4lo3U+mFM9WWyBHGuFkkxQpvSujo=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c h1:o+f69x7YeWAAW3UV1c+T2jSRr0nB8tNyZEEbufDMNi4=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c/go.mod h1:HIpGvF6nKCdtZ30xhdkKWGM9+4Z4CVqJH8ZBL1FTEiY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 h1:NK8TluG1JtjUt+g9HlyFtlJkfysTc2fhuxGA9NiZKwY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9/go.mod h1:kYEark+msACtYT027qNRx1NoQCCy94WNMSQxmUKOLWI=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 h1:osscyk2QY5FZjfd6lDbQu4fkovmoCSB4gOrF7AoCrEY=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3/go.mod h1:gCfn7vgwB6CB9KNVZtRCwfmgUY9MY79sgKJry+dfkZ4=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0 h1:jdftGHqULouQ1bTc92C+PDF6reypEWwdbvG//5yYI0U=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0/go.mod h1:q99H9vcMJDs6T+zsSI8XJZd6PUkZnyG3iaRbrYNUCTk=
 github.com/smartcontractkit/chainlink-testing-framework/havoc v1.50.5 h1:S5HND0EDtlA+xp2E+mD11DlUTp2wD6uojwixye8ZB/k=
```

### integration-tests/load/go.mod
```diff
@@ -459,7 +459,7 @@ require (
 	github.com/smartcontractkit/chainlink-protos/rmn/v1.6/go v0.0.0-20250131130834-15e0d4cde2a6 // indirect
 	github.com/smartcontractkit/chainlink-protos/svr v1.1.0 // indirect
 	github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c // indirect
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 // indirect
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/lib/grafana v1.51.0 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/parrot v0.6.2 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/sentinel v0.1.2 // indirect
```

### integration-tests/load/go.sum
```diff
@@ -1498,8 +1498,8 @@ github.com/smartcontractkit/chainlink-protos/svr v1.1.0 h1:79Z9N9dMbMVRGaLoDPAQ+
 github.com/smartcontractkit/chainlink-protos/svr v1.1.0/go.mod h1:TcOliTQU6r59DwG4lo3U+mFM9WWyBHGuFkkxQpvSujo=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c h1:o+f69x7YeWAAW3UV1c+T2jSRr0nB8tNyZEEbufDMNi4=
 github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c/go.mod h1:HIpGvF6nKCdtZ30xhdkKWGM9+4Z4CVqJH8ZBL1FTEiY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 h1:NK8TluG1JtjUt+g9HlyFtlJkfysTc2fhuxGA9NiZKwY=
-github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9/go.mod h1:kYEark+msACtYT027qNRx1NoQCCy94WNMSQxmUKOLWI=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 h1:osscyk2QY5FZjfd6lDbQu4fkovmoCSB4gOrF7AoCrEY=
+github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3/go.mod h1:gCfn7vgwB6CB9KNVZtRCwfmgUY9MY79sgKJry+dfkZ4=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0 h1:jdftGHqULouQ1bTc92C+PDF6reypEWwdbvG//5yYI0U=
 github.com/smartcontractkit/chainlink-testing-framework/framework v0.9.0/go.mod h1:q99H9vcMJDs6T+zsSI8XJZd6PUkZnyG3iaRbrYNUCTk=
 github.com/smartcontractkit/chainlink-testing-framework/havoc v1.50.5 h1:S5HND0EDtlA+xp2E+mD11DlUTp2wD6uojwixye8ZB/k=
```

### plugins/plugins.public.yaml
```diff
@@ -29,7 +29,7 @@ plugins:
 
   solana:
     - moduleURI: "github.com/smartcontractkit/chainlink-solana"
-      gitRef: "v1.1.2-0.20250611193111-99542a0c5d58"
+      gitRef: "v1.1.2-0.20250625213849-112165c2aed3"
       installPath: "github.com/smartcontractkit/chainlink-solana/pkg/solana/cmd/chainlink-solana"
 
   starknet:
```

### system-tests/lib/go.mod
```diff
@@ -373,7 +373,7 @@ require (
 	github.com/smartcontractkit/chainlink-protos/rmn/v1.6/go v0.0.0-20250131130834-15e0d4cde2a6 // indirect
 	github.com/smartcontractkit/chainlink-protos/svr v1.1.0 // indirect
 	github.com/smartcontractkit/chainlink-protos/workflows/go v0.0.0-20250619160901-79b609b1021c // indirect
-	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250616223948-ca6f14c333e9 // indirect
+	github.com/smartcontractkit/chainlink-solana v1.1.2-0.20250625213849-112165c2aed3 // indirect
 	github.com/smartcontractkit/chainlink-testing-framework/parrot v0.6.2 // indirect
 	github.com/smartcontractkit/chainlink-tron/relayer v0.0.11-0.20250528121202-292529af39df // indirect
 	github.com/smartcontractkit/freeport v0.1.1 // indirect
```

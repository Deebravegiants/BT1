# [?] Bump chainlink-evm to fix EVM TXM stack overflow (#20582)

## Summary
Severity: Unknown
Chain: Chainlink
Component: smartcontractkit/chainlink
Published: 2025-12-10
Source: https://github.com/smartcontractkit/chainlink/commit/fd1eb82750b55570de221a97d0af2f05da110026
Type: security-commit

## Details
Bump chainlink-evm to fix EVM TXM stack overflow (#20582)

## Patch
### core/scripts/go.mod
```diff
@@ -50,7 +50,7 @@ require (
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19
 	github.com/smartcontractkit/chainlink-deployments-framework v0.70.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20251124151448-0448aefdaab9
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.17.0
@@ -496,7 +496,7 @@ require (
 	github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.10 // indirect
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 // indirect
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 // indirect
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 // indirect
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 // indirect
 	github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a // indirect
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 // indirect
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4 // indirect
```

### core/scripts/go.sum
```diff
@@ -1644,16 +1644,16 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0 h1:wo2KL2viGZK/LhHLM8F88sRyhZF9wwWh+YDzW8hS00g=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0/go.mod h1:Cp7PuO7HUDugp7bWGP/TcDAvvvkFLdKOVrSm0zXlnhg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

### deployment/go.mod
```diff
@@ -44,7 +44,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20250912190424-fd2e35d7deb5
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-deployments-framework v0.70.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20251124151448-0448aefdaab9
@@ -419,7 +419,7 @@ require (
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19 // indirect
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 // indirect
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 // indirect
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 // indirect
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 // indirect
 	github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a // indirect
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4 // indirect
 	github.com/smartcontractkit/chainlink-protos/chainlink-ccv/go v0.0.0-20251126123859-d079d6815edb // indirect
```

### deployment/go.sum
```diff
@@ -1368,16 +1368,16 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0 h1:wo2KL2viGZK/LhHLM8F88sRyhZF9wwWh+YDzW8hS00g=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0/go.mod h1:Cp7PuO7HUDugp7bWGP/TcDAvvvkFLdKOVrSm0zXlnhg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

### go.mod
```diff
@@ -88,11 +88,11 @@ require (
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-common/pkg/chipingress v0.0.10
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20251124151448-0448aefdaab9
```

### go.sum
```diff
@@ -1134,16 +1134,16 @@ github.com/smartcontractkit/chainlink-common/pkg/monitoring v0.0.0-2025041523564
 github.com/smartcontractkit/chainlink-common/pkg/monitoring v0.0.0-20250415235644-8703639403c7/go.mod h1:yaDOAZF6MNB+NGYpxGCUc+owIdKrjvFW0JODdTcQ3V0=
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19 h1:gU4suSMid2uQVSxdtPhqGR9s9w3ViclcGtwkQaNbrtM=
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

### integration-tests/go.mod
```diff
@@ -53,7 +53,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20250912190424-fd2e35d7deb5
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-deployments-framework v0.70.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.17.0
 	github.com/smartcontractkit/chainlink-sui v0.0.0-20251205161630-88314452254c
@@ -501,7 +501,7 @@ require (
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19 // indirect
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 // indirect
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 // indirect
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 // indirect
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 // indirect
 	github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a // indirect
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 // indirect
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4 // indirect
```

### integration-tests/go.sum
```diff
@@ -1611,16 +1611,16 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0 h1:wo2KL2viGZK/LhHLM8F88sRyhZF9wwWh+YDzW8hS00g=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0/go.mod h1:Cp7PuO7HUDugp7bWGP/TcDAvvvkFLdKOVrSm0zXlnhg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

### integration-tests/load/go.mod
```diff
@@ -34,7 +34,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana/gobindings v0.0.0-20250912190424-fd2e35d7deb5
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-deployments-framework v0.70.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-testing-framework/framework v0.12.1
 	github.com/smartcontractkit/chainlink-testing-framework/havoc v1.50.5
@@ -486,7 +486,7 @@ require (
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19 // indirect
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 // indirect
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 // indirect
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 // indirect
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 // indirect
 	github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a // indirect
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 // indirect
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4 // indirect
```

### integration-tests/load/go.sum
```diff
@@ -1590,16 +1590,16 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0 h1:wo2KL2viGZK/LhHLM8F88sRyhZF9wwWh+YDzW8hS00g=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0/go.mod h1:Cp7PuO7HUDugp7bWGP/TcDAvvvkFLdKOVrSm0zXlnhg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

### system-tests/lib/go.mod
```diff
@@ -35,7 +35,7 @@ require (
 	github.com/smartcontractkit/chainlink-ccip/chains/solana v0.0.0-20250912190424-fd2e35d7deb5
 	github.com/smartcontractkit/chainlink-common v0.9.6-0.20251125103916-0b41e73b80c4
 	github.com/smartcontractkit/chainlink-deployments-framework v0.70.0
-	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5
+	github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec
 	github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b
 	github.com/smartcontractkit/chainlink-protos/cre/go v0.0.0-20251124151448-0448aefdaab9
 	github.com/smartcontractkit/chainlink-protos/job-distributor v0.17.0
@@ -460,7 +460,7 @@ require (
 	github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19 // indirect
 	github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 // indirect
 	github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 // indirect
-	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 // indirect
+	github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 // indirect
 	github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a // indirect
 	github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 // indirect
 	github.com/smartcontractkit/chainlink-protos/billing/go v0.0.0-20251024234028-0988426d98f4 // indirect
```

### system-tests/lib/go.sum
```diff
@@ -1607,16 +1607,16 @@ github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12
 github.com/smartcontractkit/chainlink-data-streams v0.1.7-0.20251209111830-ccd12a5b2a19/go.mod h1:GPsn6PKJvPe1UfRYyVxsDzOWq6NILzBstiiLq/w+kG0=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0 h1:wo2KL2viGZK/LhHLM8F88sRyhZF9wwWh+YDzW8hS00g=
 github.com/smartcontractkit/chainlink-deployments-framework v0.70.0/go.mod h1:Cp7PuO7HUDugp7bWGP/TcDAvvvkFLdKOVrSm0zXlnhg=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5 h1:C1iBjGqdrju2sgsbUeaePmibmC+DRRFVTRKbTVBIWp0=
-github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251208160518-8173bbd516d5/go.mod h1:OQCmZCKnOiNp7LVbHAr6xZ9SThAU7jx5uI+aCvLOn1Q=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec h1:K8sLjgwPgozQb86LH+aWXqBUJak6VGwSt5YiKbCI/uY=
+github.com/smartcontractkit/chainlink-evm v0.3.4-0.20251210110629-10c56e8d2cec/go.mod h1:9VcrUs+H/f9ekkqAdfUd70Pk2dA1Zc3KykJVFBfJNHs=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b h1:Dqhm/67Sb1ohgce8FW6tnK1CRXo2zoLCbV+EGyew5sg=
 github.com/smartcontractkit/chainlink-evm/gethwrappers v0.0.0-20251022075638-49d961001d1b/go.mod h1:oyfOm4k0uqmgZIfxk1elI/59B02shbbJQiiUdPdbMgI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135 h1:8u9xUrC+yHrTDexOKDd+jrA6LCzFFHeX1G82oj2fsSI=
 github.com/smartcontractkit/chainlink-feeds v0.1.2-0.20250227211209-7cd000095135/go.mod h1:NkvE4iQgiT7dMCP6U3xPELHhWhN5Xr6rHC0axRebyMU=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563 h1:ACpDbAxG4fa4sA83dbtYcrnlpE/y7thNIZfHxTv2ZLs=
 github.com/smartcontractkit/chainlink-framework/capabilities v0.0.0-20250818175541-3389ac08a563/go.mod h1:jP5mrOLFEYZZkl7EiCHRRIMSSHCQsYypm1OZSus//iI=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942 h1:D7N2d46Nj7ZSzpdDRg6GtsgldNgZyOojjWrH/Y/Fl+w=
-github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251021173435-e86785845942/go.mod h1:+pRGfDej1r7cHMs1dYmuyPuOZzYB9Q+PKu0FvZOYlmw=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15 h1:Mf+IRvrXutcKAKpuOxq5Ae+AAw4Z5vc66q1xI7qimZQ=
+github.com/smartcontractkit/chainlink-framework/chains v0.0.0-20251210101658-1c5c8e4c4f15/go.mod h1:kGprqyjsz6qFNVszOQoHc24wfvCjyipNZFste/3zcbs=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a h1:pr0VFI7AWlDVJBEkcvzXWd97V8w8QMNjRdfPVa/IQLk=
 github.com/smartcontractkit/chainlink-framework/metrics v0.0.0-20251020150604-8ab84f7bad1a/go.mod h1:jo+cUqNcHwN8IF7SInQNXDZ8qzBsyMpnLdYbDswviFc=
 github.com/smartcontractkit/chainlink-framework/multinode v0.0.0-20251021173435-e86785845942 h1:T/eCDsUI8EJT4n5zSP4w1mz4RHH+ap8qieA17QYfBhk=
```

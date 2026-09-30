# [?] fix race condition

## Summary
Severity: Unknown
Chain: Polygon CDK
Component: 0xPolygon/cdk
Published: 2024-07-15
Source: https://github.com/0xPolygon/cdk/commit/c75d071e2b66d7aabc8b12663d21f1199d28e86f
Type: security-commit

## Details
fix race condition

## Patch
### test/Makefile
```diff
@@ -6,4 +6,4 @@ generate-mocks-localbridgesync: ## Generates mocks for localbridgesync , using m
 	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/mockery --name=EthClienter --dir=../localbridgesync --output=../localbridgesync --outpkg=localbridgesync --inpackage --structname=L2Mock --filename=mock_l2_test.go
 	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/mockery --name=downloaderInterface --dir=../localbridgesync --output=../localbridgesync --outpkg=localbridgesync --inpackage --structname=DownloaderMock --filename=mock_downloader_test.go
 	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/mockery --name=processorInterface --dir=../localbridgesync --output=../localbridgesync --outpkg=localbridgesync --inpackage --structname=ProcessorMock --filename=mock_processor_test.go
-	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/mockery --name=reorgDetectorInterface --dir=../localbridgesync --output=../localbridgesync --outpkg=localbridgesync --inpackage --structname=ReorgDetectorMock --filename=mock_reorgdetector_test.go
\ No newline at end of file
+	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/mockery --name=ReorgDetector --dir=../localbridgesync --output=../localbridgesync --outpkg=localbridgesync --inpackage --structname=ReorgDetectorMock --filename=mock_reorgdetector_test.go
\ No newline at end of file
```

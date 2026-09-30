# [?] fix bug and remove race condition check

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/relayer
Published: 2020-07-14
Source: https://github.com/cosmos/relayer/commit/a89bd0c7789a3fe5d6333d57502f8dd3260cb771
Type: security-commit

## Details
fix bug and remove race condition check

## Patch
### Makefile
```diff
@@ -39,22 +39,22 @@ install: go.sum
 # Tests / CI
 ###############################################################################
 test:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/...
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/...
 
 test-gaia:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/... -run TestGaia*
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/... -run TestGaia*
 
 test-mtd:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/... -run TestMtd*
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/... -run TestMtd*
 
 test-rocketzone:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/... -run TestRocket*
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/... -run TestRocket*
 
 test-agoric:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/... -run TestAgoric*
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/... -run TestAgoric*
 
 test-coco:
-	@TEST_DEBUG=true go test -mod=readonly -v -race ./test/... -run TestCoCo*
+	@TEST_DEBUG=true go test -mod=readonly -v ./test/... -run TestCoCo*
 
 coverage:
 	@echo "viewing test coverage..."
```

### relayer/query.go
```diff
@@ -1238,7 +1238,7 @@ func ParseEvents(e string) ([]string, error) {
 
 	var tmEvents = make([]string, len(events))
 
-	for _, event := range events {
+	for i, event := range events {
 		if !strings.Contains(event, "=") {
 			return []string{}, fmt.Errorf("invalid event; event %s should be of the format: %s", event, eventFormat)
 		} else if strings.Count(event, "=") > 1 {
@@ -1252,7 +1252,7 @@ func ParseEvents(e string) ([]string, error) {
 			event = fmt.Sprintf("%s='%s'", tokens[0], tokens[1])
 		}
 
-		tmEvents = append(tmEvents, event)
+		tmEvents[i] = event
 	}
 	return tmEvents, nil
 }
```

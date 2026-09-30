# [?] Merge branch 'master' into peterargue/fix-follower-happy-path-pebble-panic

## Summary
Severity: Unknown
Chain: Flow
Component: onflow/flow-go
Published: 2026-04-10
Source: https://github.com/onflow/flow-go/commit/0c84502633bb2a7abbd9a40d557fc49765d063b1
Type: security-commit

## Details
Merge branch 'master' into peterargue/fix-follower-happy-path-pebble-panic

## Patch
### .github/workflows/actions/test-monitor-process-results/action.yml
```diff
@@ -42,13 +42,13 @@ runs:
       uses: 'google-github-actions/setup-gcloud@v2'
 
     - name: Upload results to BigQuery (skipped tests)
-      uses: nick-fields/retry@v3
+      uses: nick-fields/retry@v4
       with:
         timeout_minutes: 1
         max_attempts: 3
         command: bq load --source_format=NEWLINE_DELIMITED_JSON $BIGQUERY_DATASET.$BIGQUERY_TABLE $SKIPPED_TESTS_FILE tools/test_monitor/schemas/skipped_tests_schema.json
     - name: Upload results to BigQuery (test run)
-      uses: nick-fields/retry@v3
+      uses: nick-fields/retry@v4
       with:
         timeout_minutes: 2
         max_attempts: 3
```

### .github/workflows/ci.yml
```diff
@@ -17,6 +17,7 @@ on:
   merge_group:
     branches:
       - master
+  workflow_dispatch:
 
 env:
   GO_VERSION: "1.25"
@@ -28,18 +29,18 @@ concurrency:
 jobs:
   build-linter:
     name: Build Custom Linter
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     steps:
       - name: Check out code
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Set up Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
       - name: Cache custom linter binary
         id: cache-linter
-        uses: actions/cache@v3
+        uses: actions/cache@v5
         with:
           # Key should change whenever implementation (tools/structwrite), or compilation config (.custom-gcl.yml) changes
           # When the key is different, it is a cache miss, and the custom linter binary is recompiled
@@ -68,20 +69,20 @@ jobs:
       matrix:
         dir: [./, ./integration/, ./insecure/]
     name: Lint
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     needs: build-linter # must wait for custom linter binary to be available
     steps:
     - name: Checkout repo
-      uses: actions/checkout@v4
+      uses: actions/checkout@v6
     - name: Setup Go
-      uses: actions/setup-go@v5
+      uses: actions/setup-go@v6
       timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
       with:
         go-version: ${{ env.GO_VERSION }}
         cache: true
     - name: Restore custom linter binary from cache
       id: cache-linter
-      uses: actions/cache@v3
+      uses: actions/cache@v5
       with:
         # See "Cache custom linter binary" job for information about the key structure
         key: custom-linter-${{ env.GO_VERSION }}-${{ runner.os }}-${{ hashFiles('.custom-gcl.yml', 'tools/structwrite/**') }}-${{ github.sha }}
@@ -114,10 +115,10 @@ jobs:
 
   tidy:
     name: Tidy
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
 
       - name: Setup private build environment
         if: ${{ vars.PRIVATE_BUILDS_SUPPORTED == 'true' }} 
@@ -126,7 +127,7 @@ jobs:
           cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
@@ -138,14 +139,14 @@ jobs:
 
   create-dynamic-test-matrix:
     name: Create Dynamic Test Matrix
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     outputs:
       dynamic-matrix: ${{ steps.set-test-matrix.outputs.dynamicMatrix }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
@@ -156,14 +157,14 @@ jobs:
 
   create-insecure-dynamic-test-matrix:
     name: Create Dynamic Unit Test Insecure Package Matrix
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     outputs:
       dynamic-matrix: ${{ steps.set-test-matrix.outputs.dynamicMatrix }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
@@ -174,14 +175,14 @@ jobs:
 
   create-integration-dynamic-test-matrix:
     name: Create Dynamic Integration Test Package Matrix
-    runs-on: ubuntu-latest
+    runs-on: blacksmith-4vcpu-ubuntu-2404
     outputs:
       dynamic-matrix: ${{ steps.set-test-matrix.outputs.dynamicMatrix }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
@@ -201,7 +202,7 @@ jobs:
     runs-on: ${{ matrix.targets.runner }}
     steps:
     - name: Checkout repo
-      uses: actions/checkout@v4
+      uses: actions/checkout@v6
 
     - name: Setup private build environment
       if: ${{ vars.PRIVATE_BUILDS_SUPPORTED == 'true' }} 
@@ -210,15 +211,15 @@ jobs:
         cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
     - name: Setup Go
-      uses: actions/setup-go@v5
+      uses: actions/setup-go@v6
       timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
       with:
         go-version: ${{ env.GO_VERSION }}
         cache: true
     - name: Setup tests (${{ matrix.targets.name }})
       run: VERBOSE=1 make -e GO_TEST_PACKAGES="${{ matrix.targets.packages }}" install-tools
     - name: Run tests (${{ matrix.targets.name }})
-      uses: nick-fields/retry@v3
+      uses: nick-fields/retry@v4
       with:
         timeout_minutes: 35
         max_attempts: 5
@@ -247,7 +248,7 @@ jobs:
     runs-on: ${{ matrix.targets.runner }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
 
       - name: Setup private build environment
         if: ${{ vars.PRIVATE_BUILDS_SUPPORTED == 'true' }} 
@@ -256,15 +257,15 @@ jobs:
           cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
       - name: Setup tests (${{ matrix.targets.name }})
         run: VERBOSE=1 make -e GO_TEST_PACKAGES="${{ matrix.targets.packages }}" install-tools
       - name: Run tests (${{ matrix.targets.name }})
-        uses: nick-fields/retry@v3
+        uses: nick-fields/retry@v4
         with:
           timeout_minutes: 35
           max_attempts: 5
@@ -284,12 +285,12 @@ jobs:
 
   docker-build:
     name: Docker Build
-    runs-on: buildjet-16vcpu-ubuntu-2204
+    runs-on: blacksmith-16vcpu-ubuntu-2404
     env:
       CADENCE_DEPLOY_KEY: ${{ secrets.CADENCE_DEPLOY_KEY }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
         with:
           # all tags are needed for integration tests
           fetch-depth: 0
@@ -301,14 +302,14 @@ jobs:
           cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
 
       - name: Login to Docker Hub
-        uses: docker/login-action@v3
+        uses: docker/login-action@v4
         with:
           username: ${{ vars.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}
@@ -336,7 +337,7 @@ jobs:
           gcr.io/flow-container-registry/execution-corrupted:latest \
           gcr.io/flow-container-registry/verification-corrupted:latest > flow-docker-images.tar
       - name: Cache Docker images
-        uses: actions/cache@v4
+        uses: actions/cache@v5
         with:
           path: flow-docker-images.tar
           # use the workflow run id as part of the cache key to ensure these docker images will only be used for a single workflow run
@@ -354,7 +355,7 @@ jobs:
 
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       
       - name: Setup private build environment
         if: ${{ vars.PRIVATE_BUILDS_SUPPORTED == 'true' }} 
@@ -363,15 +364,15 @@ jobs:
           cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
       - name: Setup tests (${{ matrix.targets.name }})
         run: VERBOSE=1 make -e GO_TEST_PACKAGES="${{ matrix.targets.packages }}" install-tools
       - name: Run tests (${{ matrix.targets.name }})
-        uses: nick-fields/retry@v3
+        uses: nick-fields/retry@v4
         with:
           timeout_minutes: 35
           max_attempts: 5
@@ -398,60 +399,60 @@ jobs:
         include:
           - name: Access Cohort1 Integration Tests
             make: make -C integration access-cohort1-tests
-            runner: buildjet-4vcpu-ubuntu-2204
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Access Cohort2 Integration Tests
             make: make -C integration access-cohort2-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Access Cohort3 Integration Tests
             make: make -C integration access-cohort3-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Access Cohort4 Integration Tests
             make: make -C integration access-cohort4-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
             # test suite has single test which is flaky and needs to be fixed - reminder here to put it back when it's fixed
 #          - name: BFT (Framework) Integration Tests
 #            make: make -C integration bft-framework-tests
-#            runner: ubuntu-latest
+#            runner: blacksmith-4vcpu-ubuntu-2404
           - name: BFT (Protocol) Integration Tests
             make: make -C integration bft-protocol-tests
-            runner: buildjet-8vcpu-ubuntu-2204
+            runner: blacksmith-8vcpu-ubuntu-2404
           - name: BFT (Gossipsub) Integration Tests
             make: make -C integration bft-gossipsub-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Collection Integration Tests
             make: make -C integration collection-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Consensus Integration Tests
             make: make -C integration consensus-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Epoch Cohort1 Integration Tests
             make: make -C integration epochs-cohort1-tests
-            runner: buildjet-8vcpu-ubuntu-2204
+            runner: blacksmith-8vcpu-ubuntu-2404
           - name: Epoch Cohort2 Integration Tests
             make: make -C integration epochs-cohort2-tests
-            runner: buildjet-4vcpu-ubuntu-2204
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Execution Integration Tests
             make: make -C integration execution-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Ghost Integration Tests
             make: make -C integration ghost-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: MVP Integration Tests
             make: make -C integration mvp-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Network Integration Tests
             make: make -C integration network-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Verification Integration Tests
             make: make -C integration verification-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
           - name: Upgrade Integration Tests
             make: make -C integration upgrades-tests
-            runner: ubuntu-latest
+            runner: blacksmith-4vcpu-ubuntu-2404
     runs-on: ${{ matrix.runner }}
     steps:
     - name: Checkout repo
-      uses: actions/checkout@v4
+      uses: actions/checkout@v6
       with:
           # all tags are needed for integration tests
           fetch-depth: 0
@@ -463,13 +464,13 @@ jobs:
         cadence_deploy_key: ${{ secrets.CADENCE_DEPLOY_KEY }}
 
     - name: Setup Go
-      uses: actions/setup-go@v5
+      uses: actions/setup-go@v6
       timeout-minutes: 10 # fail fast. sometimes this step takes an extremely long time
       with:
         go-version: ${{ env.GO_VERSION }}
         cache: true
     - name: Load cached Docker images
-      uses: actions/cache@v4
+      uses: actions/cache@v5
       with:
         path: flow-docker-images.tar
         # use the same cache key as the docker-build job
@@ -480,7 +481,7 @@ jobs:
       # TODO(rbtz): re-enable when we fix exisiting races.
       #env:
       #  RACE_DETECTOR: 1
-      uses: nick-fields/retry@v3
+      uses: nick-fields/retry@v4
       with:
         timeout_minutes: 35
         max_attempts: 5
```

### .github/workflows/code-analysis.yml
```diff
@@ -28,10 +28,10 @@ jobs:
         languages: ['go']
     steps:
       - name: Checkout repository
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
 
       - name: Setup Go
-        uses: actions/setup-go@v4
+        uses: actions/setup-go@v6
         with:
             go-version-file: ./go.mod
 
@@ -43,7 +43,7 @@ jobs:
 
 
       - name: Initialize CodeQL
-        uses: github/codeql-action/init@v3
+        uses: github/codeql-action/init@v4
         with:
           languages: ${{ matrix.languages}}
           queries: security-extended
@@ -52,7 +52,7 @@ jobs:
         run: CGO_ENABLED=0 go build -mod=vendor -tags=no_cgo ./... 
 
       - name: CodeQL Analyze 
-        uses: github/codeql-action/analyze@v3
+        uses: github/codeql-action/analyze@v4
         with:
           category: "/language:${{ matrix.languages}}"
-          # need org username and pat to access private libraries
\ No newline at end of file
+          # need org username and pat to access private libraries
```

### .github/workflows/dependency-review.yml
```diff
@@ -10,6 +10,11 @@ on:
   pull_request:
     branches: ["master"]
 
+# Until actions/dependency-review-action ships node24 in action.yml, opt in per GitHub guidance:
+# https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/
+env:
+  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
+
 permissions:
   contents: read
   pull-requests: write # Required for PR comments
@@ -21,7 +26,7 @@ jobs:
       vulnerable-changes: ${{ steps.review.outputs.vulnerable-changes }}
     steps:
       - name: "Checkout repository"
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: "Dependency Review"
         id: review
         uses: actions/dependency-review-action@v4
@@ -36,7 +41,7 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Add PR Comment
-        uses: actions/github-script@v7
+        uses: actions/github-script@v8
         env:
           VULN_OUTPUT: ${{ needs.dependency-review.outputs.vulnerable-changes }}
         with:
@@ -72,4 +77,4 @@ jobs:
             } catch (error) {
               console.error('Error processing vulnerability data:', error);
               throw error;
-            }
\ No newline at end of file
+            }
```

### .github/workflows/flaky-test-monitor.yml
```diff
@@ -37,9 +37,9 @@ jobs:
       dynamic-matrix: ${{ steps.set-test-matrix.outputs.dynamicMatrix }}
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
@@ -58,9 +58,9 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
@@ -100,9 +100,9 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
@@ -160,12 +160,12 @@ jobs:
     runs-on: ubuntu-latest
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v4
+        uses: actions/checkout@v6
         with:
           # all tags are needed for integration tests
           fetch-depth: 0
       - name: Setup Go
-        uses: actions/setup-go@v5
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
           cache: true
```

### .github/workflows/image_builds.yml
```diff
@@ -80,27 +80,27 @@ jobs:
     environment: container builds
     steps:
       - name: Setup Go
-        uses: actions/setup-go@v4
+        uses: actions/setup-go@v6
         with:
           go-version: ${{ env.GO_VERSION }}
 
       - name: Checkout Public flow-go repo
-        uses: actions/checkout@v3
+        uses: actions/checkout@v6
         with:
           fetch-depth: 0
           repository: onflow/flow-go
           ref: ${{ inputs.tag }}
 
       - name: Authenticate with Docker Registry
-        uses: google-github-actions/auth@v1
+        uses: google-github-actions/auth@v3
         with:
           credentials_json: ${{ secrets.GCP_CREDENTIALS_FOR_PRIVATE_REGISTRY }}
 
       - name: Setup Google Cloud Authentication
         run: gcloud auth configure-docker ${{ env.PRIVATE_REGISTRY_HOST }}
 
       - name: Login to Docker Hub
-        uses: docker/login-action@v3
+        uses: docker/login-action@v4
         with:
           username: ${{ vars.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}
@@ -117,7 +117,8 @@ jobs:
     # It uses a matrix strategy to handle the builds for different roles in parallel.
     # The environment is set to 'secure builds' to ensure that the builds are gated and only approved images are deployed.
     # The job is triggered only if the 'secure-build' input is set to 'true'.
-    # The job uses an action to execute a cross-repo workflow that builds and pushes the images to the private registry.
+    # max-parallel: 1 ensures each role gets the correct run ID (avoids wrong run mapping when polling).
+    # Set vars.SECURE_BUILDS_REPO (e.g. flow-go-internal) for unmasked run links in logs.
     name: Execute secure build & push to private registry
     runs-on: ubuntu-latest
     if: ${{ github.event.inputs.secure-build == 'true' }}
@@ -135,6 +136,7 @@ jobs:
           owner: ${{ github.repository_owner }}
 
       - uses: convictional/trigger-workflow-and-wait@v1.6.5
+        id: trigger-secure-build
         with:
           client_payload: '{"role": "${{ matrix.role }}", "tag": "${{ inputs.tag }}"}'
           github_token: ${{ steps.app-token.outputs.token }}
@@ -143,6 +145,11 @@ jobs:
           ref: master-private
           workflow_file_name: 'secure_build.yml'
 
+      - name: Print secure build run URL
+        run: |
+          REPO="${{ vars.SECURE_BUILDS_REPO || 'flow-go-internal' }}"
+          echo "Secure build for ${{ matrix.role }}: https://github.com/onflow/${REPO}/actions/runs/${{ steps.trigger-secure-build.outputs.workflow_id }}"
+
   promote-to-partner-registry:
     # This job promotes container images from the private registry to the partner registry.
     # As of right now, the only role being promoted to the partner registry is 'access'.
@@ -164,7 +171,7 @@ jobs:
     environment: ${{ matrix.role }} image promotion to partner registry
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v3
+        uses: actions/checkout@v6
 
       - name: Promote ${{ matrix.role }}
         uses: ./actions/promote-images
@@ -196,7 +203,7 @@ jobs:
     environment: ${{ matrix.role }} image promotion to public registry
     steps:
       - name: Checkout repo
-        uses: actions/checkout@v3
+        uses: actions/checkout@v6
 
       - name: Promote ${{ matrix.role }}
         uses: ./actions/promote-images
```

### .github/workflows/tools.yml
```diff
@@ -24,19 +24,19 @@ jobs:
     - name: Print all input variables
       run: echo '${{ toJson(inputs) }}' | jq
     - id: auth
-      uses: google-github-actions/auth@v1
+      uses: google-github-actions/auth@v3
       with:
         credentials_json: ${{ secrets.GCR_SERVICE_KEY }}
     - name: Set up Google Cloud SDK
-      uses: google-github-actions/setup-gcloud@v1
+      uses: google-github-actions/setup-gcloud@v3
       with:
         project_id: flow
     - name: Setup Go
-      uses: actions/setup-go@v5
+      uses: actions/setup-go@v6
       with:
         go-version: ${{ env.GO_VERSION }}
     - name: Checkout repo
-      uses: actions/checkout@v4
+      uses: actions/checkout@v6
       with:
         # to accurately get the version tag
         fetch-depth: 0
```

### AGENTS.md
```diff
@@ -86,6 +86,14 @@ Note: this repo includes 2 go modules:
 - **Verification Node** (`/cmd/verification/`) - Execution result verification
 - **Observer Node** (`/cmd/observer/`) - Read-only network participant
 
+Abbreviations:
+- **AN**: Access Node
+- **LN**: Collection Node
+- **SN**: Consensus Node
+- **EN**: Execution Node
+- **VN**: Verification Node
+- **ON**: Observer Node
+
 ### Core Components
 
 #### Consensus (HotStuff/Jolteon)
```

### access/api.go
```diff
@@ -99,13 +99,31 @@ type TransactionStreamAPI interface {
 	) subscription.Subscription
 }
 
+// ReceiptsAPI provides access to execution receipts for blocks and execution results.
+type ReceiptsAPI interface {
+	// GetExecutionReceiptsByBlockID retrieves all known execution receipts for the given block.
+	//
+	// Expected error returns during normal operation:
+	//   - codes.NotFound: if no receipts are indexed for the given block ID.
+	GetExecutionReceiptsByBlockID(ctx context.Context, blockID flow.Identifier) ([]*flow.ExecutionReceipt, error)
+
+	// GetExecutionReceiptsByResultID retrieves all known execution receipts that commit to the
+	// given execution result ID. It resolves the associated block ID from the result, then
+	// retrieves all receipts for that block, filtering to those matching the requested result.
+	//
+	// Expected error returns during normal operation:
+	//   - codes.NotFound: if the execution result or its block's receipts are not found.
+	GetExecutionReceiptsByResultID(ctx context.Context, resultID flow.Identifier) ([]*flow.ExecutionReceipt, error)
+}
+
 // API provides all public-facing functionality of the Flow Access API.
 type API interface {
 	AccountsAPI
 	EventsAPI
 	ScriptsAPI
 	TransactionsAPI
 	TransactionStreamAPI
+	ReceiptsAPI
 
 	Ping(ctx context.Context) error
 	GetNetworkParameters(ctx context.Context) accessmodel.NetworkParameters
```

### access/backends/extended/api.go
```diff
@@ -9,16 +9,18 @@ import (
 	"github.com/onflow/flow-go/model/flow"
 )
 
-// API defines the extended access API for querying account transaction history.
+// API defines the extended access API for querying account transaction and transfer history.
 type API interface {
 	// GetAccountTransactions returns a paginated list of transactions for the given account address.
 	// Results are ordered descending by block height (newest first).
 	//
 	// If the account is found but has no transactions, the response will include an empty array and no error.
 	//
 	// Expected error returns during normal operations:
+	//   - [codes.NotFound] if the account is not found
 	//   - [codes.FailedPrecondition] if the account transaction index has not been initialized
 	//   - [codes.OutOfRange] if the cursor references a height outside the indexed range
+	//   - [codes.InvalidArgument] if the query parameters are invalid
 	GetAccountTransactions(
 		ctx context.Context,
 		address flow.Address,
@@ -28,4 +30,145 @@ type API interface {
 		expandOptions AccountTransactionExpandOptions,
 		encodingVersion entities.EventEncodingVersion,
 	) (*accessmodel.AccountTransactionsPage, error)
+
+	// GetAccountFungibleTokenTransfers returns a paginated list of fungible token transfers for
+	// the given account address. Results are ordered descending by block height (newest first).
+	//
+	// If the account has no transfers, the response will include an empty array and no error.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.NotFound] if the account is not found
+	//   - [codes.FailedPrecondition] if the fungible token transfer index has not been initialized
+	//   - [codes.OutOfRange] if the cursor references a height outside the indexed range
+	//   - [codes.InvalidArgument] if the query parameters are invalid
+	GetAccountFungibleTokenTransfers(
+		ctx context.Context,
+		address flow.Address,
+		limit uint32,
+		cursor *accessmodel.TransferCursor,
+		filter AccountTransferFilter,
+		expandOptions AccountTransferExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.FungibleTokenTransfersPage, error)
+
+	// GetAccountNonFungibleTokenTransfers returns a paginated list of non-fungible token transfers
+	// for the given account address. Results are ordered descending by block height (newest first).
+	//
+	// If the account has no transfers, the response will include an empty array and no error.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.NotFound] if the account is not found
+	//   - [codes.FailedPrecondition] if the non-fungible token transfer index has not been initialized
+	//   - [codes.OutOfRange] if the cursor references a height outside the indexed range
+	//   - [codes.InvalidArgument] if the query parameters are invalid
+	GetAccountNonFungibleTokenTransfers(
+		ctx context.Context,
+		address flow.Address,
+		limit uint32,
+		cursor *accessmodel.TransferCursor,
+		filter AccountTransferFilter,
+		expandOptions AccountTransferExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.NonFungibleTokenTransfersPage, error)
+
+	// GetScheduledTransaction returns a single scheduled transaction by its scheduler-assigned ID.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.NotFound]: if no transaction with the given ID exists
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	GetScheduledTransaction(
+		ctx context.Context,
+		id uint64,
+		expandOptions ScheduledTransactionExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ScheduledTransaction, error)
+
+	// GetScheduledTransactions returns a paginated list of scheduled transactions.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	//   - [codes.InvalidArgument]: if the query parameters are invalid
+	GetScheduledTransactions(
+		ctx context.Context,
+		limit uint32,
+		cursor *accessmodel.ScheduledTransactionCursor,
+		filter ScheduledTransactionFilter,
+		expandOptions ScheduledTransactionExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ScheduledTransactionsPage, error)
+
+	// GetScheduledTransactionsByAddress returns a paginated list of scheduled transactions for the given address.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	//   - [codes.InvalidArgument]: if the query parameters are invalid
+	GetScheduledTransactionsByAddress(
+		ctx context.Context,
+		address flow.Address,
+		limit uint32,
+		cursor *accessmodel.ScheduledTransactionCursor,
+		filter ScheduledTransactionFilter,
+		expandOptions ScheduledTransactionExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ScheduledTransactionsPage, error)
+
+	// GetContract returns the most recent deployment of the given contract.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.NotFound]: if no contract with the given identifier exists
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	GetContract(
+		ctx context.Context,
+		id string,
+		filter ContractDeploymentFilter,
+		expandOptions ContractDeploymentExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ContractDeployment, error)
+
+	// GetContractDeployments returns a paginated list of all deployments of the given contract,
+	// most recent first.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.NotFound]: if no contract with the given identifier exists
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	//   - [codes.InvalidArgument]: if query parameters are invalid
+	GetContractDeployments(
+		ctx context.Context,
+		id string,
+		limit uint32,
+		cursor *accessmodel.ContractDeploymentsCursor,
+		filter ContractDeploymentFilter,
+		expandOptions ContractDeploymentExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ContractDeploymentPage, error)
+
+	// GetContracts returns a paginated list of contracts at their latest deployment.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	//   - [codes.InvalidArgument]: if query parameters are invalid
+	GetContracts(
+		ctx context.Context,
+		limit uint32,
+		cursor *accessmodel.ContractDeploymentsCursor,
+		filter ContractDeploymentFilter,
+		expandOptions ContractDeploymentExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ContractDeploymentPage, error)
+
+	// GetContractsByAddress returns a paginated list of contracts at their latest deployment for
+	// the given address.
+	//
+	// Expected error returns during normal operations:
+	//   - [codes.FailedPrecondition]: if the index has not been initialized
+	//   - [codes.InvalidArgument]: if query parameters are invalid
+	GetContractsByAddress(
+		ctx context.Context,
+		address flow.Address,
+		limit uint32,
+		cursor *accessmodel.ContractDeploymentsCursor,
+		filter ContractDeploymentFilter,
+		expandOptions ContractDeploymentExpandOptions,
+		encodingVersion entities.EventEncodingVersion,
+	) (*accessmodel.ContractDeploymentPage, error)
 }
```

### access/backends/extended/backend.go
```diff
@@ -1,16 +1,22 @@
 package extended
 
 import (
+	"context"
+	"errors"
 	"fmt"
 
 	"github.com/rs/zerolog"
+	"google.golang.org/grpc/codes"
+	"google.golang.org/grpc/status"
 
 	"github.com/onflow/flow-go/engine/access/index"
 	"github.com/onflow/flow-go/engine/access/rpc/backend/transactions/error_messages"
 	"github.com/onflow/flow-go/engine/access/rpc/backend/transactions/provider"
-	"github.com/onflow/flow-go/engine/access/rpc/backend/transactions/status"
+	txstatus "github.com/onflow/flow-go/engine/access/rpc/backend/transactions/status"
 	"github.com/onflow/flow-go/model/access/systemcollection"
 	"github.com/onflow/flow-go/model/flow"
+	"github.com/onflow/flow-go/module/execution"
+	"github.com/onflow/flow-go/module/irrecoverable"
 	"github.com/onflow/flow-go/state/protocol"
 	"github.com/onflow/flow-go/storage"
 )
@@ -29,9 +35,12 @@ func DefaultConfig() Config {
 	}
 }
 
-// Backend implements the extended API for querying account transactions.
+// Backend implements the extended API for querying account transactions and token transfers.
 type Backend struct {
 	*AccountTransactionsBackend
+	*AccountTransfersBackend
+	*ScheduledTransactionsBackend
+	*ContractsBackend
 
 	log zerolog.Logger
 }
@@ -44,6 +53,8 @@ func New(
 	config Config,
 	chainID flow.ChainID,
 	store storage.AccountTransactionsReader,
+	ftStore storage.FungibleTokenTransfersBootstrapper,
+	nftStore storage.NonFungibleTokenTransfersBootstrapper,
 	state protocol.State,
 	blocks storage.Blocks,
 	headers storage.Headers,
@@ -53,7 +64,10 @@ func New(
 	collections storage.CollectionsReader,
 	transactions storage.TransactionsReader,
 	scheduledTransactions storage.ScheduledTransactionsReader,
-	txStatusDeriver *status.TxStatusDeriver,
+	scheduledTxIndex storage.ScheduledTransactionsIndexReader,
+	contractsIndex storage.ContractDeploymentsIndexReader,
+	txStatusDeriver *txstatus.TxStatusDeriver,
+	scriptExecutor execution.ScriptExecutor,
 ) (*Backend, error) {
 	log = log.With().Str("component", "extended_backend").Logger()
 
@@ -74,18 +88,40 @@ func New(
 		chainID,
 	)
 
+	base := &backendBase{
+		config:                config,
+		headers:               headers,
+		blocks:                blocks,
+		collections:           collections,
+		transactions:          transactions,
+		scheduledTransactions: scheduledTransactions,
+		systemCollections:     systemCollections,
+		transactionsProvider:  transactionsProvider,
+	}
+
+	chain := chainID.Chain()
 	return &Backend{
-		log: log,
-		AccountTransactionsBackend: NewAccountTransactionsBackend(
-			log,
-			config,
-			store,
-			headers,
-			collections,
-			transactions,
-			scheduledTransactions,
-			systemCollections,
-			transactionsProvider,
-		),
+		log:                          log,
+		AccountTransactionsBackend:   NewAccountTransactionsBackend(log, base, store, chain),
+		AccountTransfersBackend:      NewAccountTransfersBackend(log, base, ftStore, nftStore, chain),
+		ScheduledTransactionsBackend: NewScheduledTransactionsBackend(log, base, chainID, scheduledTxIndex, contractsIndex, scheduledTransactions, state, scriptExecutor),
+		ContractsBackend:             NewContractsBackend(log, base, contractsIndex),
 	}, nil
 }
+
+// mapReadError converts storage read errors to appropriate gRPC status errors.
+func mapReadError(ctx context.Context, label string, err error) error {
+	switch {
+	case errors.Is(err, storage.ErrNotBootstrapped):
+		return status.Errorf(codes.FailedPrecondition, "%s index not initialized: %v", label, err)
+	case errors.Is(err, storage.ErrHeightNotIndexed):
+		return status.Errorf(codes.OutOfRange, "requested height not indexed: %v", err)
+	case errors.Is(err, storage.ErrInvalidQuery):
+		return status.Errorf(codes.InvalidArgument, "invalid query: %v", err)
+	case errors.Is(err, storage.ErrNotFound):
+		return status.Errorf(codes.NotFound, "not found: %v", err)
+	default:
+		irrecoverable.Throw(ctx, fmt.Errorf("failed to get %s: %w", label, err))
+		return err
+	}
+}
```

### access/backends/extended/backend_account_transactions.go
```diff
@@ -2,21 +2,19 @@ package extended
 
 import (
 	"context"
-	"errors"
 	"fmt"
 
+	"github.com/rs/zerolog"
 	"google.golang.org/grpc/codes"
 	"google.golang.org/grpc/status"
 
 	"github.com/onflow/flow/protobuf/go/flow/entities"
-	"github.com/rs/zerolog"
 
-	"github.com/onflow/flow-go/engine/access/rpc/backend/transactions/provider"
 	accessmodel "github.com/onflow/flow-go/model/access"
-	"github.com/onflow/flow-go/model/access/systemcollection"
 	"github.com/onflow/flow-go/model/flow"
 	"github.com/onflow/flow-go/module/irrecoverable"
 	"github.com/onflow/flow-go/storage"
+	"github.com/onflow/flow-go/storage/indexes/iterator"
 )
 
 type AccountTransactionExpandOptions struct {
@@ -54,41 +52,25 @@ func (f *AccountTransactionFilter) Filter() storage.IndexFilter[*accessmodel.Acc
 
 // AccountTransactionsBackend implements the extended API for querying account transactions.
 type AccountTransactionsBackend struct {
-	log    zerolog.Logger
-	config Config
-	store  storage.AccountTransactionsReader
+	*backendBase
 
-	headers               storage.Headers
-	collections           storage.CollectionsReader
-	transactions          storage.TransactionsReader
-	scheduledTransactions storage.ScheduledTransactionsReader
-
-	transactionsProvider provider.TransactionProvider
-	systemCollections    *systemcollection.Versioned
+	log   zerolog.Logger
+	store storage.AccountTransactionsReader
+	chain flow.Chain
 }
 
-// New creates a new AccountTransactionsBackend instance.
+// NewAccountTransactionsBackend creates a new AccountTransactionsBackend instance.
 func NewAccountTransactionsBackend(
 	log zerolog.Logger,
-	config Config,
+	base *backendBase,
 	store storage.AccountTransactionsReader,
-	headers storage.Headers,
-	collections storage.CollectionsReader,
-	transactions storage.TransactionsReader,
-	scheduledTransactions storage.ScheduledTransactionsReader,
-	systemCollections *systemcollection.Versioned,
-	transactionsProvider provider.TransactionProvider,
+	chain flow.Chain,
 ) *AccountTransactionsBackend {
 	return &AccountTransactionsBackend{
-		log:                   log,
-		config:                config,
-		store:                 store,
-		headers:               headers,
-		collections:           collections,
-		transactions:          transactions,
-		scheduledTransactions: scheduledTransactions,
-		systemCollections:     systemCollections,
-		transactionsProvider:  transactionsProvider,
+		backendBase: base,
+		log:         log,
+		store:       store,
+		chain:       chain,
 	}
 }
 
@@ -98,8 +80,10 @@ func NewAccountTransactionsBackend(
 // If the account is found but has no transactions, the response will include an empty array and no error.
 //
 // Expected error returns during normal operations:
+//   - [codes.NotFound] if the account is not found
 //   - [codes.FailedPrecondition] if the account transaction index has not been initialized
 //   - [codes.OutOfRange] if the cursor references a height outside the indexed range
+//   - [codes.InvalidArgument] if the query parameters are invalid
 func (b *AccountTransactionsBackend) GetAccountTransactions(
 	ctx context.Context,
 	address flow.Address,
@@ -109,32 +93,37 @@ func (b *AccountTransactionsBackend) GetAccountTransactions(
 	expandOptions AccountTransactionExpandOptions,
 	encodingVersion entities.EventEncodingVersion,
 ) (*accessmodel.AccountTransactionsPage, error) {
-	if limit == 0 {
-		limit = b.config.DefaultPageSize
+	limit, err := b.normalizeLimit(limit)
+	if err != nil {
+		return nil, status.Errorf(codes.InvalidArgument, "invalid limit: %v", err)
 	}
-	if limit > b.config.MaxPageSize {
-		limit = b.config.MaxPageSize
+
+	if !b.chain.IsValid(address) {
+		return nil, status.Errorf(codes.NotFound, "account %s is not valid on chain %s", address, b.chain.ChainID())
 	}
+	// TODO: check if account exists for the chain
 
-	page, err := b.store.TransactionsByAddress(address, limit, cursor, filter.Filter())
+	iter, err := b.store.ByAddress(address, cursor)
 	if err != nil {
-		switch {
-		case errors.Is(err, storage.ErrNotBootstrapped):
-			return nil, status.Errorf(codes.FailedPrecondition, "account transaction index not initialized: %v", err)
-		case errors.Is(err, storage.ErrHeightNotIndexed):
-			return nil, status.Errorf(codes.OutOfRange, "requested height not indexed: %v", err)
-		default:
-			irrecoverable.Throw(ctx, fmt.Errorf("failed to get account transactions: %w", err))
-			return nil, err
-		}
+		return nil, mapReadError(ctx, "account transactions", err)
+	}
+
+	collected, nextCursor, err := iterator.CollectResults(iter, limit, filter.Filter())
+	if err != nil {
+		err = fmt.Errorf("error collecting transactions: %w", err)
+		irrecoverable.Throw(ctx, err)
+		return nil, err
+	}
+
+	page := accessmodel.AccountTransactionsPage{
+		Transactions: collected,
+		NextCursor:   nextCursor,
 	}
 
-	// enrich the transactions with additional details requested by the client
-	// Note: if no transactions are found, the response will include an empty array and no error.
 	for i := range page.Transactions {
-		err := b.enrichTransaction(ctx, &page.Transactions[i], expandOptions, encodingVersion)
-		if err != nil {
-			err = fmt.Errorf("failed to populate details for transaction %s: %w", page.Transactions[i].TransactionID, err)
+		tx := &page.Transactions[i]
+		if err := b.expand(ctx, tx, expandOptions, encodingVersion); err != nil {
+			err = fmt.Errorf("unexpected error expanding transaction: %w", err)
 			irrecoverable.Throw(ctx, err)
 			return nil, err
 		}
@@ -143,24 +132,19 @@ func (b *AccountTransactionsBackend) GetAccountTransactions(
 	return &page, nil
 }
 
-// enrichTransaction adds additional details to the transaction.
+// expand adds additional details to the transaction.
 //
 // Since the extended indexer only indexes sealed data, all transaction and result data should exist
 // in storage for the given height.
 //
 // No error returns are expected during normal operation.
-func (b *AccountTransactionsBackend) enrichTransaction(
+func (b *AccountTransactionsBackend) expand(
 	ctx context.Context,
 	tx *accessmodel.AccountTransaction,
 	expandOptions AccountTransactionExpandOptions,
 	encodingVersion entities.EventEncodingVersion,
 ) error {
-	blockID, err := b.headers.BlockIDByHeight(tx.BlockHeight)
-	if err != nil {
-		return fmt.Errorf("could not retrieve block ID: %w", err)
-	}
-
-	header, err := b.headers.ByBlockID(blockID)
+	header, err := b.headers.ByHeight(tx.BlockHeight)
 	if err != nil {
 		return fmt.Errorf("could not retrieve block header: %w", err)
 	}
@@ -193,113 +177,3 @@ func (b *AccountTransactionsBackend) enrichTransaction(
 
 	return nil
 }
-
-// getTransactionBody retrieves the transaction body for the given txID by searching in order:
-// submitted transactions, system transactions, and finally scheduled transactions.
-// The second return value indicates whether the transaction is a system transaction
-// (system chunk or scheduled execution).
-//
-// If the transaction is a scheduled transaction, the block ID stored for it must match the
-// provided header. A mismatch indicates an inconsistency in the node's storage, which is
-// treated as an irrecoverable exception.
-//
-// Similarly, if the transaction was indexed for an account but cannot be found in any storage
-// location, the node's state is inconsistent, which is also treated as an irrecoverable
-// exception.
-//
-// No error returns are expected during normal operation.
-func (b *AccountTransactionsBackend) getTransactionBody(ctx context.Context, header *flow.Header, txID flow.Identifier) (*flow.TransactionBody, bool, error) {
-	// first, check if it's a submitted transaction since that's the most common
-	txBody, err := b.transactions.ByID(txID)
-	if err == nil {
-		return txBody, false, nil
-	}
-	if !errors.Is(err, storage.ErrNotFound) {
-		return nil, false, fmt.Errorf("failed to retrieve transaction body: %w", err)
-	}
-
-	// next, check if the transaction is a system transaction because it's the cheapest lookup
-	systemTx, ok := b.systemCollections.SearchAll(txID)
-	if ok {
-		return systemTx, true, nil
-	}
-
-	// finally, check if it's a scheduled transaction
-	blockID, err := b.scheduledTransactions.BlockIDByTransactionID(txID)
-	if err != nil {
-		if errors.Is(err, storage.ErrNotFound) {
-			return nil, false, fmt.Errorf("transaction not found: %w", err)
-		}
-		return nil, false, fmt.Errorf("could not retrieve scheduled transaction block ID: %w", err)
-	}
-
-	// the provided header was looked up based on data stored in the db for the account transaction.
-	// if the transaction is a scheduled transaction, it must match the block ID indexed for the
-	// scheduled transaction, otherwise the node is in an inconsistent state.
-	if blockID != header.ID() {
-		err := fmt.Errorf("scheduled transaction found in block %s, but %s was provided", blockID, header.ID())
-		irrecoverable.Throw(ctx, err)
-		return nil, false, err
-	}
-
-	allScheduledTxs, err := b.transactionsProvider.ScheduledTransactionsByBlockID(ctx, header)
-	if err != nil {
-		return nil, false, fmt.Errorf("could not retrieve all scheduled transactions: %w", err)
-	}
-
-	for _, scheduledTx := range allScheduledTxs {
-		if scheduledTx.ID() == txID {
-			return scheduledTx, true, nil
-		}
-	}
-
-	// at this point, the transaction is not known to the node.
-	// this is unexpected. if the account transaction was indexed, then the transaction should be found
-	// somewhere in storage.
-	err = fmt.Errorf("indexed transaction not found")
-	irrecoverable.Throw(ctx, err)
-	return nil, false, err
-}
-
-// getTransactionResult retrieves the transaction result for a given transaction.
-//
-// Expected error returns during normal operation:
-//   - [storage.ErrNotFound] if the transaction is not found
-func (b *AccountTransactionsBackend) getTransactionResult(
-	ctx context.Context,
-	txID flow.Identifier,
-	header *flow.Header,
-	isSystemChunkTx bool,
-	expandTransaction bool,
-	encodingVersion entities.EventEncodingVersion,
-) (*accessmodel.TransactionResult, error) {
-	// the system collection is not indexed and uses the zero ID by convention.
-	var collectionID flow.Identifier
-
-	if !isSystemChunkTx {
-		collection, err := b.collections.LightByTransactionID(txID)
-		if err != nil {
-			if !errors.Is(err, storage.ErrNotFound) {
-				return nil, fmt.Errorf("could not retrieve collection: %w", err)
-			}
-			// if we have already looked up the transaction and confirmed it is NOT a system chunk tx,
-			// then there should be an entry in the tx/collection index. however, the collection/tx
-			// index is built asynchronously with the extended indexer and may not be available yet.
-			// return an error, but don't throw an irrecoverable error.
-			if expandTransaction {
-				return nil, fmt.Errorf("could not retrieve collection for standard transaction: %w", err)
-			}
-			// if the collection is not found and we're not expanding the transaction,
-			// proceed with zero collectionID.
-		} else {
-			collectionID = collection.ID()
-		}
-	}
-
-	result, err := b.transactionsProvider.TransactionResult(ctx, header, txID, collectionID, encodingVersion)
-	if err != nil {
-		return nil, fmt.Errorf("could not retrieve transaction result: %w", err)
-	}
-
-	return result, nil
-}
```

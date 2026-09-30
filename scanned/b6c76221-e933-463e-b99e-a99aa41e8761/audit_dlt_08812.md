# [?] Merge branch 'develop' into improve/websocket-server-dos-prevention

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-node
Published: 2023-08-21
Source: https://github.com/0xPolygon/zkevm-node/commit/8c82b18ed4e90b6359892e5415fc205c7c69dc69
Type: security-commit

## Details
Merge branch 'develop' into improve/websocket-server-dos-prevention

## Patch
### .github/workflows/jsonschema.yml
```diff
@@ -0,0 +1,61 @@
+---
+name: JSON schema
+on:
+  push:
+    branches:
+      - main
+      - master
+      - develop
+      - update-external-dependencies
+      - 'release/**'
+  pull_request:
+
+jobs:
+  json-schema:
+    strategy:
+      matrix:
+        go-version: [ 1.19.x ]
+        goarch: [ "amd64" ]
+    runs-on: ubuntu-latest
+    steps:
+    - name: Checkout code
+      uses: actions/checkout@v3
+      # https://github.com/actions/checkout#Checkout-pull-request-HEAD-commit-instead-of-merge-commit
+      # Checkout pull request HEAD commit instead of merge commit
+      with:
+        ref: ${{ github.event.pull_request.head.sha }}
+
+    - name: Install Go
+      uses: actions/setup-go@v3
+      with:
+        go-version: ${{ matrix.go-version }}
+      env:
+        GOARCH: ${{ matrix.goarch }}
+
+    - uses: actions/setup-python@v1
+    - uses: BSFishy/pip-action@v1
+      with:
+        packages: |
+          json-schema-for-humans
+
+    - name: Check if JSON schema and generated doc is up to date
+      run: |
+          EXPECTED_DIFF=""
+          NOT_UPDATED_MSG="JSON Schema is not up to date, run 'make config-doc-gen' before creating the PR"
+
+          echo "Checking if JSON schema is up to date..."
+          make GENERATE_DOC_PATH=/tmp/ config-doc-gen
+          for CHECK_FILE in "node-config-schema.json" "node-config-doc.md" "node-config-doc.html" "custom_network-config-schema.json" "custom_network-config-doc.md" "custom_network-config-doc.html"; do
+            EXPECTED_FILE=tmp/$CHECK_FILE
+            REAL_FILE=docs/config-file/$CHECK_FILE
+            echo "checking $CHECK_FILE ...."
+            diff /tmp/$CHECK_FILE docs/config-file/$CHECK_FILE
+            if [ $? -ne 0  ]; then
+              echo "  FAILED file $CHECK_FILE!"
+              exit 1
+            fi
+            echo "checked $CHECK_FILE OK"
+          done
+
+          echo "Everything up to date"
+
```

### .github/workflows/release.yml
```diff
@@ -46,12 +46,12 @@ jobs:
           sed -i -e "s/image: zkevm-node/image: hermeznetwork\/zkevm-node:$GIT_TAG_NAME/g" testnet/docker-compose.yml
           zip -r testnet.zip testnet
           # MAINNET
-          mkdir -p mainnet/config/environments/testnet
+          mkdir -p mainnet/config/environments/mainnet
           mkdir -p mainnet/db/scripts
-          cp config/environments/mainnet/* mainnet/config/environments/testnet
+          cp config/environments/mainnet/* mainnet/config/environments/mainnet
           cp docker-compose.yml mainnet
           cp db/scripts/init_prover_db.sql mainnet/db/scripts
-          mv mainnet/config/environments/testnet/example.env mainnet
+          mv mainnet/config/environments/mainnet/example.env mainnet
           sed -i -e "s/image: zkevm-node/image: hermeznetwork\/zkevm-node:$GIT_TAG_NAME/g" mainnet/docker-compose.yml
           zip -r mainnet.zip mainnet
 
@@ -61,4 +61,4 @@ jobs:
           files: 'testnet.zip;mainnet.zip'
           repo-token: ${{ secrets.TOKEN_RELEASE }}
           release-tag: ${{ steps.tagName.outputs.tag }}
-        
\ No newline at end of file
+        
```

### .gitignore
```diff
@@ -16,4 +16,6 @@
 .env
 out.dat
 
-cmd/__debug_bin
\ No newline at end of file
+cmd/__debug_bin
+
+.venv
\ No newline at end of file
```

### CONTRIBUTING.md
```diff
@@ -2,22 +2,22 @@
 
 This document addresses how we should create PRs, give and receive reviews. The motivation is to have better code, reduce the time from creation to merge while sharing knowledge and insights that help everyone becoming better developers.
 
-Note that non of this is a hard rule, but suggestions / guidelines. Although everyone is encouraged to stick to this points as much as posible. Use your common sense if some of this do not apply well on a particular PR
+Note that non of this is a hard rule, but suggestions / guidelines. Although everyone is encouraged to stick to this points as much as possible. Use your common sense if some of this do not apply well on a particular PR
 
 ## How to create a good PR
 
 - Follow the template, unless for some reason it doesn't fit the content of the PR
 - Try hard on doing small PRs (> ~400 lines), in general is better to have 2 small PRs rather than a big one
 - Indicate clearly who should review it, ideally 2 team mates
-- Author of the PR is responsible for merging. Never do it until you have the aproval of the specified reviewers unless you have their explicit permision
+- Author of the PR is responsible for merging. Never do it until you have the approval of the specified reviewers unless you have their explicit permission
 - Introduce the purpose of the PR, for example: `Fixes the handle of ...`
 - Give brief context on why this is being done and link it to any relevant issue
 - Feel free to ask to specific team mates to review specific parts of the PR
 
 ## How to do a good review
 
-- In general it's hard to set a quality treshold for changes. A good measure for when to approve is to accept changes once the overall quality of the code has been improved (compared to the code base before the PR)
-- Try hard to avoid taking things personaly. For instance avoid using `I`, `you`, `I (don't) like`, ...
+- In general it's hard to set a quality threshold for changes. A good measure for when to approve is to accept changes once the overall quality of the code has been improved (compared to the code base before the PR)
+- Try hard to avoid taking things personally. For instance avoid using `I`, `you`, `I (don't) like`, ...
 - Ask, don’t tell. ("What about trying...?" rather than "Don’t do...")
 - Try to use positive language. You can even use emoji to clarify tone.
 - Be super clear on how confident you are when requesting changes. One way to do it is by starting the message like this:
```

### Dockerfile
```diff
@@ -12,8 +12,9 @@ RUN cd /src/db && packr2
 RUN cd /src && make build
 
 # CONTAINER FOR RUNNING BINARY
-FROM alpine:3.16.0
+FROM alpine:3.18.0
 COPY --from=build /src/dist/zkevm-node /app/zkevm-node
-COPY --from=build /src/config/environments/testnet/testnet.node.config.toml /app/example.config.toml
+COPY --from=build /src/config/environments/testnet/node.config.toml /app/example.config.toml
+RUN apk update && apk add postgresql15-client
 EXPOSE 8123
 CMD ["/bin/sh", "-c", "/app/zkevm-node run"]
```

### Makefile
```diff
@@ -4,7 +4,7 @@ ARCH := $(shell arch)
 
 ifeq ($(ARCH),x86_64)
 	ARCH = amd64
-else 
+else
 	ifeq ($(ARCH),aarch64)
 		ARCH = arm64
 	endif
@@ -20,6 +20,60 @@ LDFLAGS += -X 'github.com/0xPolygonHermez/zkevm-node.GitRev=$(GITREV)'
 LDFLAGS += -X 'github.com/0xPolygonHermez/zkevm-node.GitBranch=$(GITBRANCH)'
 LDFLAGS += -X 'github.com/0xPolygonHermez/zkevm-node.BuildDate=$(DATE)'
 
+# Variables
+VENV           = .venv
+VENV_PYTHON    = $(VENV)/bin/python
+SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
+PYTHON         = $(or $(wildcard $(VENV_PYTHON)), "install_first_venv")
+GENERATE_SCHEMA_DOC = $(VENV)/bin/generate-schema-doc
+GENERATE_DOC_PATH   = "docs/config-file/"
+GENERATE_DOC_TEMPLATES_PATH = "docs/config-file/templates/"
+
+# Check dependencies
+# Check for Go
+.PHONY: check-go
+check-go:
+	@which go > /dev/null || (echo "Error: Go is not installed" && exit 1)
+
+# Check for Docker
+.PHONY: check-docker
+check-docker:
+	@which docker > /dev/null || (echo "Error: docker is not installed" && exit 1)
+
+# Check for Docker-compose
+.PHONY: check-docker-compose
+check-docker-compose:
+	@which docker-compose > /dev/null || (echo "Error: docker-compose is not installed" && exit 1)
+
+# Check for Protoc
+.PHONY: check-protoc
+check-protoc:
+	@which protoc > /dev/null || (echo "Error: Protoc is not installed" && exit 1)
+
+# Check for Python
+.PHONY: check-python
+check-python:
+	@which python3 > /dev/null || which python > /dev/null || (echo "Error: Python is not installed" && exit 1)
+
+# Check for Curl
+.PHONY: check-curl
+check-curl:
+	@which curl > /dev/null || (echo "Error: curl is not installed" && exit 1)
+
+# Targets that require the checks
+build: check-go
+lint: check-go
+build-docker: check-docker
+build-docker-nc: check-docker
+run-rpc: check-docker check-docker-compose
+stop: check-docker check-docker-compose
+install-linter: check-go check-curl
+install-config-doc-gen: check-python
+config-doc-node: check-go check-python
+config-doc-custom_network: check-go check-python
+update-external-dependencies: check-go
+generate-code-from-proto: check-protoc
+
 .PHONY: build
 build: ## Builds the binary locally into ./dist
 	$(GOENVVARS) go build -ldflags "all=$(LDFLAGS)" -o $(GOBIN)/$(GOBINARY) $(GOCMD)
@@ -33,7 +87,7 @@ build-docker-nc: ## Builds a docker image with the node binary - but without bui
 	docker build --no-cache=true -t zkevm-node -f ./Dockerfile .
 
 .PHONY: run-rpc
-run-rpc: ## Runs all the services need to run a local zkEMV RPC node
+run-rpc: ## Runs all the services needed to run a local zkEVM RPC node
 	docker-compose up -d zkevm-state-db zkevm-pool-db
 	sleep 2
 	docker-compose up -d zkevm-prover
@@ -54,6 +108,49 @@ install-linter: ## Installs the linter
 lint: ## Runs the linter
 	export "GOROOT=$$(go env GOROOT)" && $$(go env GOPATH)/bin/golangci-lint run
 
+$(VENV_PYTHON):
+	rm -rf $(VENV)
+	$(SYSTEM_PYTHON) -m venv $(VENV)
+
+venv: $(VENV_PYTHON)
+
+# https://stackoverflow.com/questions/24736146/how-to-use-virtualenv-in-makefile
+.PHONY: install-config-doc-gen
+$(GENERATE_SCHEMA_DOC): $(VENV_PYTHON)
+	$(PYTHON) -m pip install --upgrade pip
+	$(PYTHON) -m pip install json-schema-for-humans
+
+.PHONY: config-doc-gen
+config-doc-gen: config-doc-node config-doc-custom_network ## Generate config file's json-schema for node and custom_network and documentation
+
+.PHONY: config-doc-node
+config-doc-node: $(GENERATE_SCHEMA_DOC) ## Generate config file's json-schema for node and documentation
+	go run ./cmd generate-json-schema --config-file=node --output=$(GENERATE_DOC_PATH)node-config-schema.json
+	$(GENERATE_SCHEMA_DOC) --config show_breadcrumbs=true \
+		--config footer_show_time=false \
+		--config expand_buttons=true \
+		--config custom_template_path=$(GENERATE_DOC_TEMPLATES_PATH)/js/base.html \
+		$(GENERATE_DOC_PATH)node-config-schema.json \
+		$(GENERATE_DOC_PATH)node-config-doc.html
+	$(GENERATE_SCHEMA_DOC)  --config custom_template_path=$(GENERATE_DOC_TEMPLATES_PATH)/md/base.md \
+		--config footer_show_time=false \
+		$(GENERATE_DOC_PATH)node-config-schema.json \
+		$(GENERATE_DOC_PATH)node-config-doc.md
+
+.PHONY: config-doc-custom_network
+config-doc-custom_network: $(GENERATE_SCHEMA_DOC) ## Generate config file's json-schema for custom_network and documentation
+	go run ./cmd generate-json-schema --config-file=custom_network --output=$(GENERATE_DOC_PATH)custom_network-config-schema.json
+	$(GENERATE_SCHEMA_DOC) --config show_breadcrumbs=true --config footer_show_time=false \
+		--config expand_buttons=true \
+		--config custom_template_path=$(GENERATE_DOC_TEMPLATES_PATH)/js/base.html \
+		$(GENERATE_DOC_PATH)custom_network-config-schema.json \
+		$(GENERATE_DOC_PATH)custom_network-config-doc.html
+	$(GENERATE_SCHEMA_DOC)  --config custom_template_path=$(GENERATE_DOC_TEMPLATES_PATH)/md/base.md \
+		--config footer_show_time=false \
+		--config example_format=JSON \
+		$(GENERATE_DOC_PATH)custom_network-config-schema.json \
+		$(GENERATE_DOC_PATH)custom_network-config-doc.md
+
 .PHONY: update-external-dependencies
 update-external-dependencies: ## Updates external dependencies like images, test vectors or proto files
 	go run ./scripts/cmd/... updatedeps
@@ -64,9 +161,9 @@ install-git-hooks: ## Moves hook files to the .git/hooks directory
 
 .PHONY: generate-code-from-proto
 generate-code-from-proto: ## Generates code from proto files
-	cd proto/src/proto/hashdb/v1 && protoc --proto_path=. --proto_path=../../../../include --go_out=../../../../../merkletree/pb --go-grpc_out=../../../../../merkletree/pb --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative hashdb.proto
-	cd proto/src/proto/executor/v1 && protoc --proto_path=. --go_out=../../../../../state/runtime/executor/pb --go-grpc_out=../../../../../state/runtime/executor/pb --go-grpc_opt=paths=source_relative --go_opt=paths=source_relative executor.proto
-	cd proto/src/proto/aggregator/v1 && protoc --proto_path=. --proto_path=../../../../include --go_out=../../../../../aggregator/pb --go-grpc_out=../../../../../aggregator/pb --go-grpc_opt=paths=source_relative --go_opt=paths=source_relative aggregator.proto
+	cd proto/src/proto/hashdb/v1 && protoc --proto_path=. --proto_path=../../../../include --go_out=../../../../../merkletree/hashdb --go-grpc_out=../../../../../merkletree/hashdb --go_opt=paths=source_relative --go-grpc_opt=paths=source_relative hashdb.proto
+	cd proto/src/proto/executor/v1 && protoc --proto_path=. --go_out=../../../../../state/runtime/executor --go-grpc_out=../../../../../state/runtime/executor --go-grpc_opt=paths=source_relative --go_opt=paths=source_relative executor.proto
+	cd proto/src/proto/aggregator/v1 && protoc --proto_path=. --proto_path=../../../../include --go_out=../../../../../aggregator/prover --go-grpc_out=../../../../../aggregator/prover --go-grpc_opt=paths=source_relative --go_opt=paths=source_relative aggregator.proto
 
 ## Help display.
 ## Pulls comments from beside commands and prints a nicely formatted
@@ -75,6 +172,6 @@ generate-code-from-proto: ## Generates code from proto files
 
 .PHONY: help
 help: ## Prints this help
-		@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
-		| sort \
-		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
+	@grep -h -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
+	| sort \
+	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
```

### README.md
```diff
@@ -22,7 +22,6 @@ Glossary:
 - Consolidated state: state that is proven on-chain by submitting a ZKP (Zero Knowledge Proof) that proves the execution of a sequence of the last virtual batch.
 - Invalid transaction: a transaction that can't be processed and doesn't affect the state. Note that such a transaction could be included in a virtual batch. The reason for a transaction to be invalid could be related to the Ethereum protocol (invalid nonce, not enough balance, ...) or due to limitations introduced by the zkEVM (each batch can make use of a limited amount of resources such as the total amount of keccak hashes that can be computed)
 - Reverted transaction: a transaction that is executed, but is reverted (because of smart contract logic). The main difference with *invalid transaction* is that this transaction modifies the state, at least to increment nonce of the sender.
-- Proof of Efficiency (PoE): name of the protocol used by the network, it's enforced by the [smart contracts](https://github.com/0xPolygonHermez/zkevm-contracts)
 
 ## Architecture
 
@@ -32,19 +31,21 @@ Glossary:
 
 The diagram represents the main components of the software and how they interact between them. Note that this reflects a single entity running a node, in particular a node that acts as the trusted sequencer. But there are many entities running nodes in the network, and each of these entities can perform different roles. More on this later.
 
-- (JSON) RPC: an interface that allows users (metamask, etherscan, ...) to interact with the node. Fully compatible with Ethereum RPC + some extra endpoints specifics of the network. It interacts with the `state` to get data and process transactions and with the `pool` to store transactions
+- (JSON) RPC: an HTTP interface that allows users (dApps, metamask, etherscan, ...) to interact with the node. Fully compatible with Ethereum RPC + some extra [custom endpoints](./docs/zkEVM-custom-endpoints.md) specifics of the network. It interacts with the `state` (to get data and process transactions) as well as the `pool` (to store transactions).
+- L2GasPricer: it fetches the L1 gas price and applies some formula to calculate the gas price that will be suggested for the users to use for paying fees on L2. The suggestions are stored on the `pool`, and will be consumed by the `rpc`
 - Pool: DB that stores transactions by the `RPC` to be selected/discarded by the `sequencer` later on
-- Trusted Sequencer: get transactions from the `pool`, check if they are valid by processing them using the `state`, and create sequences. Once transactions are added into the state, they are immediately available through the `rpc`. Sequences are sent to L1 using the `etherman`
-- Permissionless Sequencer: *coming soon*
+- Sequencer: responsible for building the trusted state. To do so, it gets transactions from the pool and puts them in a specific order. It needs to take care of opening and closing batches while trying to make them as full as possible. To achieve this it needs to use the executor to actually process the transaction not only to execute the state transition (and update the hashDB) but also to check the consumed resources by the transactions and the remaining resources of the batch. After executing a transaction that fits into a batch, it gets stored on the `state`. Once transactions are added into the state, they are immediately available through the `rpc`.
+- SequenceSender: gets closed batches from the `state`, tries to aggregate as many of them as possible, and at some point, decides that it's time to send those batches to L1, turning the state from trusted to virtualized. In order to send the L1 tx, it uses the `ethtxmanager`
+- EthTxManager: handles requests to send L1 transactions from `sequencesender` and `aggregator`. It takes care of dealing with the nonce of the accounts, increasing the gas price, and other actions that may be needed to ensure that L1 transactions get mined
 - Etherman: abstraction that implements the needed methods to interact with the Ethereum network and the relevant smart contracts.
-- Synchronizer: Updates the `state` by fetching data from Ethereum through the `etherman`. If the node is not a `trusted sequencer` it also updates the state with the data fetched from the `rpc` of the `trusted sequencer`. It also detects and handles reorgs that can happen if the `trusted sequencer` sends different data in the rpc vs the sequences sent to L1 (trusted vs virtual state)
+- Synchronizer: Updates the `state` (virtual batches, verified batches, forced batches, ...) by fetching data from L1 through the `etherman`. If the node is not a `trusted sequencer` it also updates the state with the data fetched from the `rpc` of the `trusted sequencer`. It also detects and handles reorgs that can happen if the `trusted sequencer` sends different data in the rpc vs the sequences sent to L1 (trusted reorg aka L2 reorg). Also handles L1 reorgs (reorgs that happen on the L1 network)
 - State: Responsible for managing the state data (batches, blocks, transactions, ...) that is stored on the `state SB`. It also handles the integration with the `executor` and the `Merkletree` service
-- State DB: persistence layer for the state data (except the Merkletree that is handled by the `Merkletree` service)
-- Aggregator: consolidates batches by generating ZKPs (Zero Knowledge proofs). To do so it gathers the necessary data that the `prover` needs as input through the `state` and sends a request to it. Once the proof is generated it's sent to Ethereum through the `etherman`
-- Prover/Executor: service that generates ZK proofs. Note that this component is not implemented in this repository, and it's treated as a "black box" from the perspective of the node. The prover/executor has two implementations: [JS reference implementation](https://github.com/0xPolygonHermez/zkevm-proverjs) and [C production-ready implementation](https://github.com/0xPolygonHermez/zkevm-prover). Although it's the same software/service, it has two very different purposes:
-  - Provide an EVM implementation that allows processing transactions and getting all needed results metadata (state root, receipts, logs, ...)
-  - Generate ZKPs
-- Merkletree: service that stores the Merkletree, containing all the account information (balances, nonces, smart contract code, and smart contract storage). This component is also not implemented in this repo and is consumed as an external service by the node. The implementation can be found [here](https://github.com/0xPolygonHermez/zkevm-prover)
+- State DB: persistence layer for the state data (except the Merkletree that is handled by the `HashDB` service), it stores informationrelated to L1 (blocks, global exit root updates, ...) and L2 (batches, L2 blocks, transactions, ...)
+- Aggregator: consolidates batches by generating ZKPs (Zero Knowledge proofs). To do so it gathers the necessary data that the `prover` needs as input through the `state` and sends a request to it. Once the proof is generated it sends a request to send an L1 tx to verify the proof and move the state from virtual to verified to the `ethtxmanager`. Note that provers connect to the aggregator and not the other way arround. The aggregator can handle multiple connected provers at once and make them work concurrently in the generation of different proofs
+- Prover/Executor/hashDB: service that generates ZK proofs. Note that this component is not implemented in this repository, and it's treated as a "black box" from the perspective of the node. The prover/executor has two implementations: [JS reference implementation](https://github.com/0xPolygonHermez/zkevm-proverjs) and [C production-ready implementation](https://github.com/0xPolygonHermez/zkevm-prover). Although it's the same software/binary, it implements three services:
+  - Executor: Provides an EVM implementation that allows processing batches as well as getting metadata (state root, transaction receipts, logs, ...) of all the needed results.
+  - Prover: Generates ZKPs for batches, batches aggregation, and final proofs.
+  - HashDB: service that stores the Merkletree, containing all the account information (balances, nonces, smart contract code, and smart contract storage)
 
 ## Roles of the network
 
@@ -80,10 +81,6 @@ Required services and components:
 
 Note that the JSON RPC is required to receive transactions. It's recommended that the JSON RPC runs on separated instances, and potentially more than one (depending on the load of the network). It's also recommended that the JSON RPC and the Sequencer don't share the same executor instance, to make sure that the sequencer has exclusive access to an executor
 
-### Permissionless sequencer
-
-TBD
-
 ### Aggregator
 
 This role can be performed by anyone.
@@ -118,6 +115,6 @@ It's recommended to use `make` for building, and testing the code, ... Run `make
 
 ## Contribute
 
-Before opening a pull request, please read this [guide](CONTRIBUTING.md)
+Before opening a pull request, please read this [guide](CONTRIBUTING.md).
 
 
```

### aggregator/aggregator.go
```diff
@@ -14,7 +14,6 @@ import (
 	"unicode"
 
 	"github.com/0xPolygonHermez/zkevm-node/aggregator/metrics"
-	"github.com/0xPolygonHermez/zkevm-node/aggregator/pb"
 	"github.com/0xPolygonHermez/zkevm-node/aggregator/prover"
 	"github.com/0xPolygonHermez/zkevm-node/config/types"
 	"github.com/0xPolygonHermez/zkevm-node/encoding"
@@ -41,12 +40,12 @@ type finalProofMsg struct {
 	proverName     string
 	proverID       string
 	recursiveProof *state.Proof
-	finalProof     *pb.FinalProof
+	finalProof     *prover.FinalProof
 }
 
 // Aggregator represents an aggregator
 type Aggregator struct {
-	pb.UnimplementedAggregatorServiceServer
+	prover.UnimplementedAggregatorServiceServer
 
 	cfg Config
 
@@ -129,7 +128,7 @@ func (a *Aggregator) Start(ctx context.Context) error {
 	}
 
 	a.srv = grpc.NewServer()
-	pb.RegisterAggregatorServiceServer(a.srv, a)
+	prover.RegisterAggregatorServiceServer(a.srv, a)
 
 	healthService := newHealthChecker()
 	grpchealth.RegisterHealthServer(a.srv, healthService)
@@ -159,7 +158,7 @@ func (a *Aggregator) Stop() {
 
 // Channel implements the bi-directional communication channel between the
 // Prover client and the Aggregator server.
-func (a *Aggregator) Channel(stream pb.AggregatorService_ChannelServer) error {
+func (a *Aggregator) Channel(stream prover.AggregatorService_ChannelServer) error {
 	metrics.ConnectedProver()
 	defer metrics.DisconnectedProver()
 
@@ -306,7 +305,7 @@ func (a *Aggregator) handleFailureToAddVerifyBatchToBeMonitored(ctx context.Cont
 }
 
 // buildFinalProof builds and return the final proof for an aggregated/batch proof.
-func (a *Aggregator) buildFinalProof(ctx context.Context, prover proverInterface, proof *state.Proof) (*pb.FinalProof, error) {
+func (a *Aggregator) buildFinalProof(ctx context.Context, prover proverInterface, proof *state.Proof) (*prover.FinalProof, error) {
 	log := log.WithFields(
 		"prover", prover.Name(),
 		"proverId", prover.ID(),
@@ -972,14 +971,14 @@ func (a *Aggregator) isSynced(ctx context.Context, batchNum *uint64) bool {
 	return true
 }
 
-func (a *Aggregator) buildInputProver(ctx context.Context, batchToVerify *state.Batch) (*pb.InputProver, error) {
+func (a *Aggregator) buildInputProver(ctx context.Context, batchToVerify *state.Batch) (*prover.InputProver, error) {
 	previousBatch, err := a.State.GetBatchByNumber(ctx, batchToVerify.BatchNumber-1, nil)
 	if err != nil && err != state.ErrStateNotSynchronized {
 		return nil, fmt.Errorf("failed to get previous batch, err: %v", err)
 	}
 
-	inputProver := &pb.InputProver{
-		PublicInputs: &pb.PublicInputs{
+	inputProver := &prover.InputProver{
+		PublicInputs: &prover.PublicInputs{
 			OldStateRoot:    previousBatch.StateRoot.Bytes(),
 			OldAccInputHash: previousBatch.AccInputHash.Bytes(),
 			OldBatchNum:     previousBatch.BatchNumber,
```

### aggregator/aggregator_test.go
```diff
@@ -10,7 +10,7 @@ import (
 	"time"
 
 	"github.com/0xPolygonHermez/zkevm-node/aggregator/mocks"
-	"github.com/0xPolygonHermez/zkevm-node/aggregator/pb"
+	"github.com/0xPolygonHermez/zkevm-node/aggregator/prover"
 	configTypes "github.com/0xPolygonHermez/zkevm-node/config/types"
 	ethmanTypes "github.com/0xPolygonHermez/zkevm-node/etherman/types"
 	"github.com/0xPolygonHermez/zkevm-node/ethtxmanager"
@@ -53,7 +53,7 @@ func TestSendFinalProof(t *testing.T) {
 		BatchNumber:      batchNum,
 		BatchNumberFinal: batchNumFinal,
 	}
-	finalProof := &pb.FinalProof{}
+	finalProof := &prover.FinalProof{}
 	cfg := Config{SenderAddress: from.Hex()}
 
 	testCases := []struct {
@@ -1000,9 +1000,9 @@ func TestTryBuildFinalProof(t *testing.T) {
 	proverName := "proverName"
 	proverID := "proverID"
 	finalProofID := "finalProofID"
-	finalProof := pb.FinalProof{
+	finalProof := prover.FinalProof{
 		Proof: "",
-		Public: &pb.PublicInputsExtended{
+		Public: &prover.PublicInputsExtended{
 			NewStateRoot:     []byte("newStateRoot"),
 			NewLocalExitRoot: []byte("newLocalExitRoot"),
 		},
```

### aggregator/interfaces.go
```diff
@@ -4,7 +4,7 @@ import (
 	"context"
 	"math/big"
 
-	"github.com/0xPolygonHermez/zkevm-node/aggregator/pb"
+	"github.com/0xPolygonHermez/zkevm-node/aggregator/prover"
 	ethmanTypes "github.com/0xPolygonHermez/zkevm-node/etherman/types"
 	"github.com/0xPolygonHermez/zkevm-node/ethtxmanager"
 	"github.com/0xPolygonHermez/zkevm-node/state"
@@ -19,11 +19,11 @@ type proverInterface interface {
 	ID() string
 	Addr() string
 	IsIdle() (bool, error)
-	BatchProof(input *pb.InputProver) (*string, error)
+	BatchProof(input *prover.InputProver) (*string, error)
 	AggregatedProof(inputProof1, inputProof2 string) (*string, error)
 	FinalProof(inputProof string, aggregatorAddr string) (*string, error)
 	WaitRecursiveProof(ctx context.Context, proofID string) (string, error)
-	WaitFinalProof(ctx context.Context, proofID string) (*pb.FinalProof, error)
+	WaitFinalProof(ctx context.Context, proofID string) (*prover.FinalProof, error)
 }
 
 // ethTxManager contains the methods required to send txs to
```

### aggregator/mocks/mock_prover.go
```diff
@@ -5,7 +5,7 @@ package mocks
 import (
 	context "context"
 
-	pb "github.com/0xPolygonHermez/zkevm-node/aggregator/pb"
+	prover "github.com/0xPolygonHermez/zkevm-node/aggregator/prover"
 	mock "github.com/stretchr/testify/mock"
 )
 
@@ -55,23 +55,23 @@ func (_m *ProverMock) AggregatedProof(inputProof1 string, inputProof2 string) (*
 }
 
 // BatchProof provides a mock function with given fields: input
-func (_m *ProverMock) BatchProof(input *pb.InputProver) (*string, error) {
+func (_m *ProverMock) BatchProof(input *prover.InputProver) (*string, error) {
 	ret := _m.Called(input)
 
 	var r0 *string
 	var r1 error
-	if rf, ok := ret.Get(0).(func(*pb.InputProver) (*string, error)); ok {
+	if rf, ok := ret.Get(0).(func(*prover.InputProver) (*string, error)); ok {
 		return rf(input)
 	}
-	if rf, ok := ret.Get(0).(func(*pb.InputProver) *string); ok {
+	if rf, ok := ret.Get(0).(func(*prover.InputProver) *string); ok {
 		r0 = rf(input)
 	} else {
 		if ret.Get(0) != nil {
 			r0 = ret.Get(0).(*string)
 		}
 	}
 
-	if rf, ok := ret.Get(1).(func(*pb.InputProver) error); ok {
+	if rf, ok := ret.Get(1).(func(*prover.InputProver) error); ok {
 		r1 = rf(input)
 	} else {
 		r1 = ret.Error(1)
@@ -159,19 +159,19 @@ func (_m *ProverMock) Name() string {
 }
 
 // WaitFinalProof provides a mock function with given fields: ctx, proofID
-func (_m *ProverMock) WaitFinalProof(ctx context.Context, proofID string) (*pb.FinalProof, error) {
+func (_m *ProverMock) WaitFinalProof(ctx context.Context, proofID string) (*prover.FinalProof, error) {
 	ret := _m.Called(ctx, proofID)
 
-	var r0 *pb.FinalProof
+	var r0 *prover.FinalProof
 	var r1 error
-	if rf, ok := ret.Get(0).(func(context.Context, string) (*pb.FinalProof, error)); ok {
+	if rf, ok := ret.Get(0).(func(context.Context, string) (*prover.FinalProof, error)); ok {
 		return rf(ctx, proofID)
 	}
-	if rf, ok := ret.Get(0).(func(context.Context, string) *pb.FinalProof); ok {
+	if rf, ok := ret.Get(0).(func(context.Context, string) *prover.FinalProof); ok {
 		r0 = rf(ctx, proofID)
 	} else {
 		if ret.Get(0) != nil {
-			r0 = ret.Get(0).(*pb.FinalProof)
+			r0 = ret.Get(0).(*prover.FinalProof)
 		}
 	}
 
```

### aggregator/prover/aggregator.pb.go
```diff
@@ -1,10 +1,10 @@
 // Code generated by protoc-gen-go. DO NOT EDIT.
 // versions:
-// 	protoc-gen-go v1.28.1
+// 	protoc-gen-go v1.30.0
 // 	protoc        v3.21.12
 // source: aggregator.proto
 
-package pb
+package prover
 
 import (
 	protoreflect "google.golang.org/protobuf/reflect/protoreflect"
@@ -247,6 +247,7 @@ type AggregatorMessage struct {
 
 	Id string `protobuf:"bytes,1,opt,name=id,proto3" json:"id,omitempty"`
 	// Types that are assignable to Request:
+	//
 	//	*AggregatorMessage_GetStatusRequest
 	//	*AggregatorMessage_GenBatchProofRequest
 	//	*AggregatorMessage_GenAggregatedProofRequest
@@ -391,6 +392,7 @@ type ProverMessage struct {
 
 	Id string `protobuf:"bytes,1,opt,name=id,proto3" json:"id,omitempty"`
 	// Types that are assignable to Response:
+	//
 	//	*ProverMessage_GetStatusResponse
 	//	*ProverMessage_GenBatchProofResponse
 	//	*ProverMessage_GenAggregatedProofResponse
@@ -1263,6 +1265,7 @@ type GetProofResponse struct {
 
 	Id string `protobuf:"bytes,1,opt,name=id,proto3" json:"id,omitempty"`
 	// Types that are assignable to Proof:
+	//
 	//	*GetProofResponse_FinalProof
 	//	*GetProofResponse_RecursiveProof
 	Proof        isGetProofResponse_Proof `protobuf_oneof:"proof"`
@@ -1981,11 +1984,11 @@ var file_aggregator_proto_rawDesc = []byte{
 	0x6f, 0x72, 0x2e, 0x76, 0x31, 0x2e, 0x50, 0x72, 0x6f, 0x76, 0x65, 0x72, 0x4d, 0x65, 0x73, 0x73,
 	0x61, 0x67, 0x65, 0x1a, 0x20, 0x2e, 0x61, 0x67, 0x67, 0x72, 0x65, 0x67, 0x61, 0x74, 0x6f, 0x72,
 	0x2e, 0x76, 0x31, 0x2e, 0x41, 0x67, 0x67, 0x72, 0x65, 0x67, 0x61, 0x74, 0x6f, 0x72, 0x4d, 0x65,
-	0x73, 0x73, 0x61, 0x67, 0x65, 0x22, 0x00, 0x28, 0x01, 0x30, 0x01, 0x42, 0x35, 0x5a, 0x33, 0x67,
+	0x73, 0x73, 0x61, 0x67, 0x65, 0x22, 0x00, 0x28, 0x01, 0x30, 0x01, 0x42, 0x39, 0x5a, 0x37, 0x67,
 	0x69, 0x74, 0x68, 0x75, 0x62, 0x2e, 0x63, 0x6f, 0x6d, 0x2f, 0x30, 0x78, 0x50, 0x6f, 0x6c, 0x79,
 	0x67, 0x6f, 0x6e, 0x48, 0x65, 0x72, 0x6d, 0x65, 0x7a, 0x2f, 0x7a, 0x6b, 0x65, 0x76, 0x6d, 0x2d,
 	0x6e, 0x6f, 0x64, 0x65, 0x2f, 0x61, 0x67, 0x67, 0x72, 0x65, 0x67, 0x61, 0x74, 0x6f, 0x72, 0x2f,
-	0x70, 0x62, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
+	0x70, 0x72, 0x6f, 0x76, 0x65, 0x72, 0x62, 0x06, 0x70, 0x72, 0x6f, 0x74, 0x6f, 0x33,
 }
 
 var (
```

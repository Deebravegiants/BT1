# [?] Merge branch 'dev' of github.com:klaytn/klaytn into klay-client-api-oob-fix

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-08-02
Source: https://github.com/kaiachain/kaia/commit/616346aecee3d44e2850b8ce3cec9b12c5c616c6
Type: security-commit

## Details
Merge branch 'dev' of github.com:klaytn/klaytn into klay-client-api-oob-fix

## Patch
### .circleci/config.yml
```diff
@@ -22,11 +22,11 @@ executors:
   test-executor:
     working_directory: /go/src/github.com/klaytn/klaytn
     docker:
-      - image: klaytn/build_base:1.2-go.1.18-solc0.8.13
+      - image: klaytn/build_base:1.2-go.1.20.6-solc0.8.13
   test-others-executor:
     working_directory: /go/src/github.com/klaytn/klaytn
     docker:
-      - image: klaytn/build_base:1.2-go.1.18-solc0.8.13
+      - image: klaytn/build_base:1.2-go.1.20.6-solc0.8.13
       - image: localstack/localstack:0.13.0
       - image: circleci/redis:6.0.8-alpine
       - name: zookeeper
@@ -42,11 +42,11 @@ executors:
   rpm-executor:
     working_directory: /go/src/github.com/klaytn/klaytn
     docker:
-      - image: klaytn/circleci-rpmbuild:1.18
+      - image: klaytn/circleci-rpmbuild:1.20.6
   default:
     working_directory: ~/go/src/github.com/klaytn/klaytn
     docker:
-      - image: cimg/go:1.18
+      - image: cimg/go:1.20.6
 
 commands:
   install-netcat:
@@ -56,33 +56,52 @@ commands:
           command: |
             apt install -y netcat
   install-golang:
+    parameters:
+      os-network:
+        type: string
+        default: "linux-amd64"
     steps:
       - run:
           name: "Install golang on machine"
+          command: | 
+            curl -O https://dl.google.com/go/go1.20.6.<< parameters.os-network >>.tar.gz
+            mkdir $HOME/go1.20.6
+            tar -C $HOME/go1.20.6 -xzf go1.20.6.<< parameters.os-network >>.tar.gz
+  install-awscli:
+    steps:
+      - run:
+          name: "Install awscli on macos machine"
           command: |
-            curl -O https://dl.google.com/go/go1.18.linux-amd64.tar.gz
-            mkdir $HOME/go1.18
-            tar -C $HOME/go1.18 -xzf go1.18.linux-amd64.tar.gz
+            brew install awscli
   install-golangci-lint:
     steps:
       - run:
           name: "Install golangci-lint"
           command: |
-            curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v1.45.2
+            curl -sSfL https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh -s -- -b $(go env GOPATH)/bin v1.52.0
   pre-build:
     description: "before build, set version"
+    parameters:
+      os-network:
+        type: string
+        default: "linux-amd64"
     steps:
       - run:
           name: "set variables"
           command: |
             export GOPATH=~/go
-            export PATH=$HOME/go1.18/go/bin:$PATH
+            export PATH=$HOME/go1.20.6/go/bin:$PATH
             pat="^v[0-9]+\.[0-9]+\.[0-9]+-rc\.[0-9]+.*"
 
             if [[ $CIRCLE_TAG =~ $pat ]]; then
               echo "this is rc version $CIRCLE_TAG"
               rc_num=$(echo $CIRCLE_TAG | cut -d '-' -f 2)
-              sed -i 's/%d.%d.%d/%d.%d.%d~'$rc_num'/' params/version.go
+              if [[ << parameters.os-network >> =~ .*"darwin".* ]]; then
+                sed -i '' 's/%d.%d.%d/%d.%d.%d~'$rc_num'/' params/version.go
+              else
+                sed -i 's/%d.%d.%d/%d.%d.%d~'$rc_num'/' params/version.go
+              fi
+
               sed -n '/%d.%d.%d/p' params/version.go
             else
               echo "this is not RC version"
@@ -93,14 +112,20 @@ commands:
     parameters:
       os-network:
         type: string
-        default: "tar-linux-amd64-all"
+        default: "linux-amd64"
+      baobab:
+        type: string
+        default: ""
     steps:
       - run:
-          name: "build new(Cross compile)"
+          name: "build and packaging"
           command: |
             export GOPATH=~/go
-            export PATH=$HOME/go1.18/go/bin:$PATH
-            make << parameters.os-network >>
+            export PATH=$HOME/go1.20.6/go/bin:$PATH
+            make all
+            for item in kcn kpn ken kscn kspn ksen kbn kgen homi; do
+              ./build/package-tar.sh << parameters.baobab >> << parameters.os-network >> $item
+            done
   upload-repo:
     description: "upload packaging tar.gz"
     parameters:
@@ -112,23 +137,25 @@ commands:
           name: "upload S3 repo"
           command: |
             export GOPATH=~/go
-            export PATH=$HOME/go1.18/go/bin:$PATH
+            export PATH=$HOME/go1.20.6/go/bin:$PATH
             KLAYTN_VERSION=$(go run build/rpm/main.go version)
             for item in << parameters.item >>; do aws s3 cp packages/${item}-*.tar.gz s3://$FRONTEND_BUCKET/packages/klaytn/$KLAYTN_VERSION/; done
   rpm-tagging:
     description: "rpm tagging for cypress"
     steps:
       - run:
           name: "rpm tagging"
-          command: make rpm-all
+          command: |
+            for item in kcn kpn ken kscn kspn ksen kbn kgen homi; do
+              ./build/package-rpm.sh $item
+            done
       - run:
           name: "upload S3 repo"
           command: |
             PLATFORM_SUFFIX=$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)
             KLAYTN_VERSION=$(go run build/rpm/main.go version)
 
-            for item in kcn kpn ken kscn kspn ksen kbn kgen homi;
-            do
+            for item in kcn kpn ken kscn kspn ksen kbn kgen homi; do
               TARGET_RPM=$(find $item-linux-x86_64/rpmbuild/RPMS/x86_64/ | awk -v pat="$item(d)?-v" '$0~pat')
               aws s3 cp $TARGET_RPM s3://$FRONTEND_BUCKET/packages/rhel/7/prod/
               aws s3 cp $TARGET_RPM s3://$FRONTEND_BUCKET/packages/klaytn/$KLAYTN_VERSION/
@@ -139,15 +166,13 @@ commands:
       - run:
           name: "rpm tagging baobab"
           command: |
-              make rpm-baobab-kcn
-              make rpm-baobab-kpn
-              make rpm-baobab-ken
+            for item in kcn kpn ken; do
+              ./build/package-rpm.sh -b $item
+            done
       - run:
           name: "upload S3 repo"
           command: |
-            for item in kcn kpn ken;
-            do
-              PLATFORM_SUFFIX=$(uname -s | tr '[:upper:]' '[:lower:]')-$(uname -m)
+            for item in kcn kpn ken; do
               TARGET_RPM=$(find $item-linux-x86_64/rpmbuild/RPMS/x86_64/ | awk -v pat="$item(d)?-baobab-v" '$0~pat')
               aws s3 cp $TARGET_RPM s3://$FRONTEND_BUCKET/packages/rhel/7/prod/
               aws s3 cp $TARGET_RPM s3://$FRONTEND_BUCKET/packages/klaytn/$KLAYTN_VERSION/
@@ -319,7 +344,7 @@ jobs:
       - run:
           name: "Build"
           command: |
-            export PATH=$HOME/go1.18/go/bin:$PATH
+            export PATH=$HOME/go1.20.6/go/bin:$PATH
             make fmt
             make all
 
@@ -446,7 +471,7 @@ jobs:
       - notify-success
       - store_artifacts:
           path: /tmp/linter_reports
-  
+
   rpc-tester-report:
     executor: test-executor
     steps:
@@ -458,7 +483,7 @@ jobs:
       - notify-success
 
   packaging-linux:
-    machine: 
+    machine:
       image: ubuntu-2004:202201-02
     resource_class: large
     working_directory: ~/go/src/github.com/klaytn/klaytn
@@ -470,7 +495,7 @@ jobs:
       - upload-repo
 
   packaging-linux-baobab:
-    machine: 
+    machine:
       image: ubuntu-2004:202201-02
     resource_class: large
     working_directory: ~/go/src/github.com/klaytn/klaytn
@@ -479,34 +504,41 @@ jobs:
       - install-golang
       - pre-build
       - build-packaging:
-          os-network: "tar-baobab-linux-amd64-all"
+          baobab: "-b"
       - upload-repo:
           item: "kcn kpn ken"
 
   packaging-darwin:
-    machine: 
-      image: ubuntu-2004:202201-02
-    resource_class: large
+    macos:
+      xcode: 14.2.0
+    resource_class: macos.x86.medium.gen2
     working_directory: ~/go/src/github.com/klaytn/klaytn
     steps:
       - checkout
-      - install-golang
-      - pre-build
+      - install-awscli
+      - install-golang:
+          os-network: "darwin-amd64"
+      - pre-build:
+          os-network: "darwin-amd64"
       - build-packaging:
-          os-network: "tar-darwin-amd64-all"
+          os-network: "darwin-amd64"
       - upload-repo
 
   packaging-darwin-baobab:
-    machine: 
-      image: ubuntu-2004:202201-02
-    resource_class: large
+    macos:
+      xcode: 14.2.0
+    resource_class: macos.x86.medium.gen2
     working_directory: ~/go/src/github.com/klaytn/klaytn
     steps:
       - checkout
-      - install-golang
-      - pre-build
+      - install-awscli
+      - install-golang:
+          os-network: "darwin-amd64"
+      - pre-build:
+          os-network: "darwin-amd64"
       - build-packaging:
-          os-network: "tar-baobab-darwin-amd64-all"
+          os-network: "darwin-amd64"
+          baobab: "-b"
       - upload-repo:
           item: "kcn kpn ken"
 
@@ -593,7 +625,7 @@ workflows:
             - tagger-verify
           filters: *filter-version-not-release
 
-      - docker/publish:
+      - docker/publish: # for dev branch
           filters:
             branches:
               only: dev
@@ -605,6 +637,23 @@ workflows:
           executor: docker/docker
           use-remote-docker: true
           remote-docker-version: 20.10.14
+          use-buildkit: true
+
+      - docker/publish: # for release versions
+          filters:
+            tags:
+              only: /^v[0-9]+\.[0-9]+\.[0-9]+/
+            branches:
+              ignore: /.*/
+          requires:
+            - pass-tests
+          extra_build_args: '--platform=linux/amd64'
+          image: klaytn/klaytn
+          tag: latest,$CIRCLE_TAG
+          executor: docker/docker
+          use-remote-docker: true
+          remote-docker-version: 20.10.14
+          use-buildkit: true
 
       - tag-verify:
           filters: *filter-only-version-tag
@@ -662,21 +711,6 @@ workflows:
           requires:
             - pass-tests
 
-      - docker/publish:
-          filters:
-            tags:
-              only: /^v[0-9]+\.[0-9]+\.[0-9]+/
-            branches:
-              ignore: /.*/
-          requires:
-            - pass-tests
-          extra_build_args: '--platform=linux/amd64'
-          image: klaytn/klaytn
-          tag: latest,$CIRCLE_TAG
-          executor: docker/docker
-          use-remote-docker: true
-          remote-docker-version: 20.10.14
-
       - major-tagging:
           filters:
             branches:
@@ -701,7 +735,7 @@ workflows:
               only: dev
     jobs:
       - linters
-  
+
   nightly-rpc:
     triggers:
       - schedule:
```

### .github/CODEOWNERS
```diff
@@ -6,7 +6,7 @@
 # @global-owner1 and @global-owner2 will be requested for
 # review when someone opens a pull request.
 #*       @global-owner1 @global-owner2
-*       @kjhman21 @KimKyungup @aidan-kwon @jeongkyun-oh
+*       @aidan-kwon @blukat29 @kjeom
 
 # Order is important; the last matching pattern takes the most
 # precedence. When someone opens a pull request that only
@@ -36,31 +36,23 @@
 # In this example, @doctocat owns any file in the `/docs`
 # directory in the root of your repository.
 #/docs/ @doctocat
-/accounts/
-/api/           @aidan-kwon @jimni1222 @sirano11 @aeharvlee @JayChoi1736
-/blockchain/    @KimKyungup @aidan-kwon @jeongkyun-oh @ehnuje
-/build/         @aidan-kwon @henry-will @nohkwak @2dvorak
-/client/        @aidan-kwon @aeharvlee @henry-will @nohkwak @hyunsooda
-/cmd/           @aidan-kwon @henry-will @nohkwak @2dvorak
-/common/
-/consensus/     @aidan-kwon @jiseongnoh @yoomee1313 @mckim19
-/console/       @aidan-kwon @jimni1222 @sirano11 @aeharvlee @JayChoi1736
-/contracts/     @kjhman21 @KimKyungup @aidan-kwon @blukat29 @ian0371 @henry-will @hyunsooda @hqjang-pepper
-/crypto/
-/datasync/      @KimKyungup @ethan-kr @jeongkyun-oh @ehnuje
-/db_migration/  @KimKyungup @ethan-kr @jeongkyun-oh @ehnuje
-/event/
-/fork/          @KimKyungup @aidan-kwon @yoomee1313
-/governance/    @aidan-kwon @blukat29 @ian0371 @yoomee1313 @mckim19
-/kerrors/
-/log/
-/metrics/
-/networks/      @KimKyungup @aidan-kwon @jiseongnoh @mckim19 @ehnuje
-/node/          @KimKyungup @aidan-kwon @ehnuje @henry-will @hyunsooda @hqjang-pepper
-/params/
-/reward/        @KimKyungup @aidan-kwon @blukat29 @ian0371
-/ser/
-/storage/       @KimKyungup @ethan-kr @jeongkyun-oh @ehnuje
-/tests/
-/utils/
-/work/          @KimKyungup @aidan-kwon @jiseongnoh @yoomee1313 @mckim19
+/api/           @kjeom @nohkwak @toniya-klaytn
+/blockchain/    @blukat29 @kjeom @ian0371
+/build/	        @blukat29 @hyunsooda @2dvorak
+/client/        @hyunsooda @kjeom @nohkwak
+/cmd/           @kjeom @ian0371
+/consensus/     @aidan-kwon @jiseongnoh @yoomee1313
+/console/       @kjeom @nohkwak @JayChoi1736
+/contracts/     @ian0371 @hyunsooda @2dvorak
+/crypto/        @blukat29 @aidan-kwon @jiseongnoh
+/datasync/      @aidan-kwon @ethan-kr @jeongkyun-oh
+/db_migration/  @ethan-kr @jeongkyun-oh @yoomee1313
+/event/	        @kjeom @JayChoi1736 @nohkwak
+/governance/    @blukat29 @ian0371 @yoomee1313
+/networks/      @kjeom @JayChoi1736 @yoomee1313
+/node/	        @blukat29 @hyunsooda @2dvorak
+/reward/        @blukat29 @ian0371
+/rlp/	        @kjeom @JayChoi1736 @nohkwak
+/snapshot/      @ethan-kr @jeongkyun-oh @yoomee1313
+/storage/       @aidan-kwon @ethan-kr @jeongkyun-oh
+/work/	        @blukat29 @yoomee1313
```

### Dockerfile
```diff
@@ -18,8 +18,17 @@ ARG KLAYTN_DISABLE_SYMBOL=0
 ENV KLAYTN_DISABLE_SYMBOL=$KLAYTN_DISABLE_SYMBOL
 
 WORKDIR $SRC_DIR
-ADD . .
-RUN make all
+# Cache default $GOMODCACHE
+COPY go.mod go.sum ./
+RUN --mount=type=cache,target=/go/pkg/mod go mod download -x
+
+# Cache default $GOCACHE
+# First 'make kcn' to populate build cache and then 'make all' in parallel
+COPY . .
+RUN --mount=type=cache,target=/root/.cache/go-build \
+    --mount=type=cache,target=/go/pkg/mod \
+    make kcn && \
+    make all -j
 
 FROM --platform=linux/amd64 ubuntu:20.04
 ARG SRC_DIR
```

### Makefile
```diff
@@ -10,65 +10,17 @@ BIN = $(shell pwd)/build/bin
 BUILD_PARAM?=install
 
 OBJECTS=kcn kpn ken kscn kspn ksen kbn kgen homi
-RPM_OBJECTS=$(foreach wrd,$(OBJECTS),rpm-$(wrd))
-RPM_BAOBAB_OBJECTS=$(foreach wrd,$(OBJECTS),rpm-baobab-$(wrd))
-TAR_LINUX_386_OBJECTS=$(foreach wrd,$(OBJECTS),tar-linux-386-$(wrd))
-TAR_LINUX_amd64_OBJECTS=$(foreach wrd,$(OBJECTS),tar-linux-amd64-$(wrd))
-TAR_DARWIN_amd64_OBJECTS=$(foreach wrd,$(OBJECTS),tar-darwin-amd64-$(wrd))
-TAR_BAOBAB_LINUX_386_OBJECTS=$(foreach wrd,$(OBJECTS),tar-baobab-linux-386-$(wrd))
-TAR_BAOBAB_LINUX_amd64_OBJECTS=$(foreach wrd,$(OBJECTS),tar-baobab-linux-amd64-$(wrd))
-TAR_BAOBAB_DARWIN_amd64_OBJECTS=$(foreach wrd,$(OBJECTS),tar-baobab-darwin-amd64-$(wrd))
 
-.PHONY: all test clean ${OBJECTS} ${RPM_OBJECTS} ${TAR_LINUX_386_OBJECTS} ${TAR_DARWIN_amd64_OBJECTS} ${TAR_LINUX_amd64_OBJECTS}
+.PHONY: all test clean ${OBJECTS}
 
 all: ${OBJECTS}
-rpm-all: ${RPM_OBJECTS}
-rpm-baobab-all: ${RPM_BAOBAB_OBJECTS}
-tar-linux-386-all: ${TAR_LINUX_386_OBJECTS}
-tar-linux-amd64-all: ${TAR_LINUX_amd64_OBJECTS}
-tar-darwin-amd64-all: ${TAR_DARWIN_amd64_OBJECTS}
-tar-baobab-linux-386-all: ${TAR_BAOBAB_LINUX_386_OBJECTS}
-tar-baobab-linux-amd64-all: ${TAR_BAOBAB_LINUX_amd64_OBJECTS}
-tar-baobab-darwin-amd64-all: ${TAR_BAOBAB_DARWIN_amd64_OBJECTS}
 
 ${OBJECTS}:
+ifeq ($(USE_ROCKSDB), 1)
+	$(GORUN) build/ci.go ${BUILD_PARAM} -tags rocksdb ./cmd/$@
+else
 	$(GORUN) build/ci.go ${BUILD_PARAM} ./cmd/$@
-
-${RPM_OBJECTS}:
-	./build/package-rpm.sh ${@:rpm-%=%}
-
-${RPM_BAOBAB_OBJECTS}:
-	./build/package-rpm.sh -b ${@:rpm-baobab-%=%}
-
-${TAR_LINUX_386_OBJECTS}:
-	$(eval BIN := ${@:tar-linux-386-%=%})
-	./build/cross-compile.sh linux-386 ${BIN}
-	./build/package-tar.sh linux-386 ${BIN}
-
-${TAR_LINUX_amd64_OBJECTS}:
-	$(eval BIN := ${@:tar-linux-amd64-%=%})
-	./build/cross-compile.sh linux-amd64 ${BIN}
-	./build/package-tar.sh linux-amd64 ${BIN}
-
-${TAR_DARWIN_amd64_OBJECTS}:
-	$(eval BIN := ${@:tar-darwin-amd64-%=%})
-	./build/cross-compile.sh darwin-amd64 ${BIN}
-	./build/package-tar.sh darwin-amd64 ${BIN}
-
-${TAR_BAOBAB_LINUX_386_OBJECTS}:
-	$(eval BIN := ${@:tar-baobab-linux-386-%=%})
-	./build/cross-compile.sh linux-386 ${BIN}
-	./build/package-tar.sh -b linux-386 ${BIN}
-
-${TAR_BAOBAB_LINUX_amd64_OBJECTS}:
-	$(eval BIN := ${@:tar-baobab-linux-amd64-%=%})
-	./build/cross-compile.sh linux-amd64 ${BIN}
-	./build/package-tar.sh -b linux-amd64 ${BIN}
-
-${TAR_BAOBAB_DARWIN_amd64_OBJECTS}:
-	$(eval BIN := ${@:tar-baobab-darwin-amd64-%=%})
-	./build/cross-compile.sh darwin-amd64 ${BIN}
-	./build/package-tar.sh -b darwin-amd64 ${BIN}
+endif
 
 abigen:
 	$(GORUN) build/ci.go ${BUILD_PARAM} ./cmd/abigen
```

### README.md
```diff
@@ -33,7 +33,7 @@ After successful build, executable binaries are installed at `build/bin/`.
 | `ken` | The CLI client for Klaytn Endpoint Node, which is the entry point into the Klaytn network (main-, test- or private net).  It can be used by other processes as a gateway into the Klaytn network via JSON RPC endpoints exposed on top of HTTP, WebSocket, gRPC, and/or IPC transports. Run `ken --help` for command-line flags. |
 | `kscn` | The CLI client for Klaytn ServiceChain Consensus Node.  Run `kscn --help` for command-line flags. |
 | `kspn` | The CLI client for Klaytn ServiceChain Proxy Node.  Run `kspn --help` for command-line flags. |
-| `ksen` | The CLI client for Klaytn ServiceChain Endopoint Node.  Run `ksen --help` for command-line flags. |
+| `ksen` | The CLI client for Klaytn ServiceChain Endpoint Node.  Run `ksen --help` for command-line flags. |
 | `kbn` | The CLI client for Klaytn Bootnode. Run `kbn --help` for command-line flags. |
 | `kgen` | The CLI client for Klaytn Nodekey Generation Tool. Run `kgen --help` for command-line flags. |
 | `homi` | The CLI client for Klaytn Helper Tool to generate initialization files. Run `homi --help` for command-line flags. |
```

### accounts/abi/abi_test.go
```diff
@@ -33,6 +33,7 @@ import (
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/common/math"
 	"github.com/klaytn/klaytn/crypto"
+	"github.com/stretchr/testify/assert"
 )
 
 const jsondata = `
@@ -763,6 +764,41 @@ func TestUnpackEvent(t *testing.T) {
 	}
 }
 
+// Testset (ABI and hexdata) was created based on this contract format.
+/*
+contract T {
+     event eventInDynamicType(uint elem1, string[3] elem2);
+     constructor() {}
+     function test123() public {
+         string[3] memory vals = ["A...","B...","C..."];
+         emit eventInDynamicType(123, vals);
+     }
+ }
+*/
+func TestUnpackEventOffsetBound(t *testing.T) {
+	const abiJSON = `[{"inputs":[],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"elem1","type":"uint256"},{"indexed":false,"internalType":"string[3]","name":"elem2","type":"string[3]"}],"name":"ev123","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"elem1","type":"uint256"},{"indexed":false,"internalType":"string[3]","name":"elem2","type":"string[3]"}],"name":"eventInDynamicType","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"bytes","name":"memo","type":"bytes"}],"name":"received","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"}],"name":"receivedAddr","type":"event"},{"inputs":[],"name":"test123","outputs":[],"stateMutability":"nonpayable","type":"function"}]`
+
+	abi, err := JSON(strings.NewReader(abiJSON))
+	assert.Nil(t, err, err)
+
+	const rawData = `000000000000000000000000000000000000000000000000000000000000007b0000000000000000000000000000000000000000000000000000000000000040000000000000000000000000000000000000000000000000000000000000006000000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000140000000000000000000000000000000000000000000000000000000000000004141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141414141410000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000354242424242424242424242424242424242424242424242424242424242424242424242424242424242424242424242424242424242000000000000000000000000000000000000000000000000000000000000000000000000000000000000684343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343434343000000000000000000000000000000000000000000000000`
+	// Modify offset value (0x40 -> 0xffff) to attemp out-of-bounds access
+	modifiedRawData := rawData[:124] + "ffff" + rawData[128:]
+
+	data, err := hex.DecodeString(modifiedRawData)
+	assert.Nil(t, err)
+
+	type evObj struct {
+		Elem1 *big.Int
+		Elem2 [3]string
+	}
+
+	var params evObj
+	err = abi.Unpack(&params, "eventInDynamicType", data)
+	// Must return error
+	assert.NotNil(t, err, err)
+}
+
 func TestUnpackEventIntoMap(t *testing.T) {
 	const abiJSON = `[{"constant":false,"inputs":[{"name":"memo","type":"bytes"}],"name":"receive","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":false,"name":"sender","type":"address"},{"indexed":false,"name":"amount","type":"uint256"},{"indexed":false,"name":"memo","type":"bytes"}],"name":"received","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"sender","type":"address"}],"name":"receivedAddr","type":"event"}]`
 	abi, err := JSON(strings.NewReader(abiJSON))
```

### accounts/abi/bind/backends/blockchain.go
```diff
@@ -0,0 +1,143 @@
+// Copyright 2023 The klaytn Authors
+// This file is part of the klaytn library.
+//
+// The klaytn library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The klaytn library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the klaytn library. If not, see <http://www.gnu.org/licenses/>.
+
+package backends
+
+import (
+	"context"
+	"math/big"
+
+	"github.com/klaytn/klaytn"
+	"github.com/klaytn/klaytn/accounts/abi/bind"
+	"github.com/klaytn/klaytn/blockchain"
+	"github.com/klaytn/klaytn/blockchain/state"
+	"github.com/klaytn/klaytn/blockchain/types"
+	"github.com/klaytn/klaytn/blockchain/vm"
+	"github.com/klaytn/klaytn/common"
+	"github.com/klaytn/klaytn/params"
+)
+
+// Maintain separate minimal interfaces of blockchain.BlockChain because ContractBackend are used
+// in various situations. BlockChain instances are often passed down as different interfaces such as
+// consensus.ChainReader, governance.blockChain, work.BlockChain.
+type BlockChainForCaller interface {
+	// Required by NewEVMContext
+	blockchain.ChainContext
+
+	// Below is a subset of consensus.ChainReader
+	// Only using the vocabulary of consensus.ChainReader for potential
+	// usability within consensus package.
+	Config() *params.ChainConfig
+	CurrentHeader() *types.Header
+	GetHeaderByNumber(number uint64) *types.Header
+	GetBlock(hash common.Hash, number uint64) *types.Block
+	State() (*state.StateDB, error)
+	StateAt(root common.Hash) (*state.StateDB, error)
+	CurrentBlock() *types.Block
+}
+
+// BlockchainContractCaller implements bind.ContractCaller, based on
+// a user-supplied blockchain.BlockChain instance.
+// Its intended purpose is reading system contracts during block processing.
+//
+// Note that SimulatedBackend creates a new temporary BlockChain for testing,
+// whereas BlockchainContractCaller uses an existing BlockChain with existing database.
+type BlockchainContractCaller struct {
+	bc BlockChainForCaller
+}
+
+// This nil assignment ensures at compile time that BlockchainContractCaller implements bind.ContractCaller.
+var _ bind.ContractCaller = (*BlockchainContractCaller)(nil)
+
+func NewBlockchainContractCaller(bc BlockChainForCaller) *BlockchainContractCaller {
+	return &BlockchainContractCaller{
+		bc: bc,
+	}
+}
+
+func (b *BlockchainContractCaller) CodeAt(ctx context.Context, account common.Address, blockNumber *big.Int) ([]byte, error) {
+	if _, state, err := b.getBlockAndState(blockNumber); err != nil {
+		return nil, err
+	} else {
+		return state.GetCode(account), nil
+	}
+}
+
+// Executes a read-only function call with respect to the specified block's state, or latest state if not specified.
+//
+// Returns call result in []byte.
+// Returns error when:
+// - cannot find the corresponding block or stateDB
+// - VM revert error
+// - VM other errors (e.g. NotProgramAccount, OutOfGas)
+// - Error outside VM
+func (b *BlockchainContractCaller) CallContract(ctx context.Context, call klaytn.CallMsg, blockNumber *big.Int) ([]byte, error) {
+	block, state, err := b.getBlockAndState(blockNumber)
+	if err != nil {
+		return nil, err
+	}
+
+	res, err := b.callContract(call, block, state)
+	if err != nil {
+		return nil, err
+	}
+	if len(res.Revert()) > 0 {
+		return nil, blockchain.NewRevertError(res)
+	}
+	return res.Return(), res.Unwrap()
+}
+
+func (b *BlockchainContractCaller) callContract(call klaytn.CallMsg, block *types.Block, state *state.StateDB) (*blockchain.ExecutionResult, error) {
+	if call.Gas == 0 {
+		call.Gas = uint64(3e8) // enough gas for ordinary contract calls
+	}
+
+	intrinsicGas, err := types.IntrinsicGas(call.Data, nil, call.To == nil, b.bc.Config().Rules(block.Number()))
+	if err != nil {
+		return nil, err
+	}
+
+	msg := types.NewMessage(call.From, call.To, 0, call.Value, call.Gas, call.GasPrice, call.Data,
+		false, intrinsicGas)
+
+	evmContext := blockchain.NewEVMContext(msg, block.Header(), b.bc, nil)
+	// EVM demands the sender to have enough KLAY balance (gasPrice * gasLimit) in buyGas()
+	// After KIP-71, gasPrice is nonzero baseFee, regardless of the msg.gasPrice (usually 0)
+	// But our sender (usually 0x0) won't have enough balance. Instead we override gasPrice = 0 here
+	evmContext.GasPrice = big.NewInt(0)
+	evm := vm.NewEVM(evmContext, state, b.bc.Config(), &vm.Config{})
+
+	return blockchain.ApplyMessage(evm, msg)
+}
+
+func (b *BlockchainContractCaller) getBlockAndState(num *big.Int) (*types.Block, *state.StateDB, error) {
+	var block *types.Block
+	if num == nil {
+		block = b.bc.CurrentBlock()
+	} else {
+		header := b.bc.GetHeaderByNumber(num.Uint64())
+		if header == nil {
+			return nil, nil, errBlockDoesNotExist
+		}
+		block = b.bc.GetBlock(header.Hash(), header.Number.Uint64())
+	}
+	if block == nil {
+		return nil, nil, errBlockDoesNotExist
+	}
+
+	state, err := b.bc.StateAt(block.Root())
+	return block, state, err
+}
```

### accounts/abi/bind/backends/blockchain_test.go
```diff
@@ -0,0 +1,149 @@
+// Copyright 2023 The klaytn Authors
+// This file is part of the klaytn library.
+//
+// The klaytn library is free software: you can redistribute it and/or modify
+// it under the terms of the GNU Lesser General Public License as published by
+// the Free Software Foundation, either version 3 of the License, or
+// (at your option) any later version.
+//
+// The klaytn library is distributed in the hope that it will be useful,
+// but WITHOUT ANY WARRANTY; without even the implied warranty of
+// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+// GNU Lesser General Public License for more details.
+//
+// You should have received a copy of the GNU Lesser General Public License
+// along with the klaytn library. If not, see <http://www.gnu.org/licenses/>.
+
+package backends
+
+import (
+	"context"
+	"errors"
+	"math/big"
+	"strings"
+	"testing"
+
+	"github.com/klaytn/klaytn"
+	"github.com/klaytn/klaytn/accounts/abi"
+	"github.com/klaytn/klaytn/blockchain"
+	"github.com/klaytn/klaytn/blockchain/vm"
+	"github.com/klaytn/klaytn/common"
+	"github.com/klaytn/klaytn/consensus/gxhash"
+	"github.com/klaytn/klaytn/crypto"
+	"github.com/klaytn/klaytn/params"
+	"github.com/klaytn/klaytn/storage/database"
+	"github.com/stretchr/testify/assert"
+)
+
+var (
+	testAddr  = crypto.PubkeyToAddress(testKey.PublicKey)
+	code1Addr = common.HexToAddress("0x1111111111111111111111111111111111111111")
+	code2Addr = common.HexToAddress("0x2222222222222222222222222222222222222222")
+
+	parsedAbi1, _ = abi.JSON(strings.NewReader(abiJSON))
+	parsedAbi2, _ = abi.JSON(strings.NewReader(reverterABI))
+	code1Bytes    = common.FromHex(deployedCode)
+	code2Bytes    = common.FromHex(reverterDeployedBin)
+)
+
+func newTestBlockchain() *blockchain.BlockChain {
+	config := params.TestChainConfig.Copy()
+	alloc := blockchain.GenesisAlloc{
+		testAddr:  {Balance: big.NewInt(10000000000)},
+		code1Addr: {Balance: big.NewInt(0), Code: code1Bytes},
+		code2Addr: {Balance: big.NewInt(0), Code: code2Bytes},
+	}
+
+	db := database.NewMemoryDBManager()
+	genesis := blockchain.Genesis{Config: config, Alloc: alloc}
+	genesis.MustCommit(db)
+
+	bc, _ := blockchain.NewBlockChain(db, nil, genesis.Config, gxhash.NewFaker(), vm.Config{})
+
+	// Append 10 blocks to test with block numbers other than 0
+	block := bc.CurrentBlock()
+	blocks, _ := blockchain.GenerateChain(config, block, gxhash.NewFaker(), db, 10, func(i int, b *blockchain.BlockGen) {})
+	bc.InsertChain(blocks)
+
+	return bc
+}
+
+func TestBlockchainCodeAt(t *testing.T) {
+	bc := newTestBlockchain()
+	c := NewBlockchainContractCaller(bc)
+
+	// Normal cases
+	code, err := c.CodeAt(context.Background(), code1Addr, nil)
+	assert.Nil(t, err)
+	assert.Equal(t, code1Bytes, code)
+
+	code, err = c.CodeAt(context.Background(), code2Addr, nil)
+	assert.Nil(t, err)
+	assert.Equal(t, code2Bytes, code)
+
+	code, err = c.CodeAt(context.Background(), code1Addr, common.Big0)
+	assert.Nil(t, err)
+	assert.Equal(t, code1Bytes, code)
+
+	code, err = c.CodeAt(context.Background(), code1Addr, common.Big1)
+	assert.Nil(t, err)
+	assert.Equal(t, code1Bytes, code)
+
+	code, err = c.CodeAt(context.Background(), code1Addr, big.NewInt(10))
+	assert.Nil(t, err)
+	assert.Equal(t, code1Bytes, code)
+
+	// Non-code address
+	code, err = c.CodeAt(context.Background(), testAddr, nil)
+	assert.True(t, code == nil && err == nil)
+
+	// Invalid block number
+	code, err = c.CodeAt(context.Background(), code1Addr, big.NewInt(11))
+	assert.True(t, code == nil && err == errBlockDoesNotExist)
+}
+
+func TestBlockchainCallContract(t *testing.T) {
+	bc := newTestBlockchain()
+	c := NewBlockchainContractCaller(bc)
+
+	data_receive, _ := parsedAbi1.Pack("receive", []byte("X"))
+	data_revertString, _ := parsedAbi2.Pack("revertString")
+	data_revertNoString, _ := parsedAbi2.Pack("revertNoString")
+
+	// Normal case
+	ret, err := c.CallContract(context.Background(), klaytn.CallMsg{
+		From: testAddr,
+		To:   &code1Addr,
+		Gas:  1000000,
+		Data: data_receive,
+	}, nil)
+	assert.Nil(t, err)
+	assert.Equal(t, expectedReturn, ret)
+
+	// Error outside VM - Intrinsic Gas
+	ret, err = c.CallContract(context.Background(), klaytn.CallMsg{
+		From: testAddr,
+		To:   &code1Addr,
+		Gas:  20000,
+		Data: data_receive,
+	}, nil)
+	assert.True(t, errors.Is(err, blockchain.ErrIntrinsicGas))
+
+	// VM revert error - empty reason
+	ret, err = c.CallContract(context.Background(), klaytn.CallMsg{
+		From: testAddr,
+		To:   &code2Addr,
+		Gas:  100000,
+		Data: data_revertNoString,
+	}, nil)
+	assert.Equal(t, "execution reverted: ", err.Error())
+
+	// VM revert error - string reason
+	ret, err = c.CallContract(context.Background(), klaytn.CallMsg{
+		From: testAddr,
+		To:   &code2Addr,
+		Gas:  100000,
+		Data: data_revertString,
+	}, nil)
+	assert.Equal(t, "execution reverted: some error", err.Error())
+}
```

### accounts/abi/bind/backends/simulated.go
```diff
@@ -52,7 +52,6 @@ var (
 	errBlockNumberUnsupported  = errors.New("simulatedBackend cannot access blocks other than the latest block")
 	errBlockDoesNotExist       = errors.New("block does not exist in blockchain")
 	errTransactionDoesNotExist = errors.New("transaction does not exist")
-	errGasEstimationFailed     = errors.New("gas required exceeds allowance or always failing transaction")
 )
 
 // SimulatedBackend implements bind.ContractBackend, simulating a blockchain in
@@ -135,7 +134,7 @@ func (b *SimulatedBackend) rollback() {
 	stateDB, _ := b.blockchain.State()
 
 	b.pendingBlock = blocks[0]
-	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil)
+	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil, nil)
 }
 
 // stateByBlockNumber retrieves a state by a given blocknumber.
@@ -366,8 +365,15 @@ func (b *SimulatedBackend) CallContract(ctx context.Context, call klaytn.CallMsg
 	if err != nil {
 		return nil, err
 	}
-	res, _, _, err := b.callContract(ctx, call, b.blockchain.CurrentBlock(), stateDB)
-	return res, err
+	res, err := b.callContract(ctx, call, b.blockchain.CurrentBlock(), stateDB)
+	if err != nil {
+		return nil, err
+	}
+	// If the result contains a revert reason, try to unpack and return it.
+	if len(res.Revert()) > 0 {
+		return nil, blockchain.NewRevertError(res)
+	}
+	return res.Return(), res.Unwrap()
 }
 
 // PendingCallContract executes a contract call on the pending state.
@@ -376,8 +382,15 @@ func (b *SimulatedBackend) PendingCallContract(ctx context.Context, call klaytn.
 	defer b.mu.Unlock()
 	defer b.pendingState.RevertToSnapshot(b.pendingState.Snapshot())
 
-	rval, _, _, err := b.callContract(ctx, call, b.pendingBlock, b.pendingState)
-	return rval, err
+	res, err := b.callContract(ctx, call, b.pendingBlock, b.pendingState)
+	if err != nil {
+		return nil, err
+	}
+	// If the result contains a revert reason, try to unpack and return it.
+	if len(res.Revert()) > 0 {
+		return nil, blockchain.NewRevertError(res)
+	}
+	return res.Return(), res.Unwrap()
 }
 
 // PendingNonceAt implements PendingStateReader.PendingNonceAt, retrieving
@@ -401,76 +414,37 @@ func (b *SimulatedBackend) EstimateGas(ctx context.Context, call klaytn.CallMsg)
 	b.mu.Lock()
 	defer b.mu.Unlock()
 
-	// Determine the lowest and highest possible gas limits to binary search in between
-	var (
-		lo  uint64 = params.TxGas - 1
-		hi  uint64
-		cap uint64
-	)
-	if call.Gas >= params.TxGas {
-		hi = call.Gas
-	} else {
-		hi = params.UpperGasLimit
-	}
-
-	// Recap the highest gas allowance with account's balance.
-	if call.GasPrice != nil && call.GasPrice.BitLen() != 0 {
-		balance := b.pendingState.GetBalance(call.From) // from can't be nil
-		available := new(big.Int).Set(balance)
-		if call.Value != nil {
-			if call.Value.Cmp(available) >= 0 {
-				return 0, errors.New("insufficient funds for transfer")
-			}
-			available.Sub(available, call.Value)
-		}
-		allowance := new(big.Int).Div(available, call.GasPrice)
-		if allowance.IsUint64() && hi > allowance.Uint64() {
-			transfer := call.Value
-			if transfer == nil {
-				transfer = new(big.Int)
-			}
-			bind.Logger.Warn("Gas estimation capped by limited funds", "original", hi, "balance", balance,
-				"sent", transfer, "gasprice", call.GasPrice, "fundable", allowance)
-			hi = allowance.Uint64()
-		}
-	}
-	cap = hi
+	balance := b.pendingState.GetBalance(call.From) // from can't be nil
 
 	// Create a helper to check if a gas allowance results in an executable transaction
-	executable := func(gas uint64) bool {
+	executable := func(gas uint64) (bool, *blockchain.ExecutionResult, error) {
 		call.Gas = gas
 
 		currentState, err := b.blockchain.State()
 		if err != nil {
-			return false
+			return true, nil, nil
 		}
-		_, _, failed, err := b.callContract(ctx, call, b.blockchain.CurrentBlock(), currentState)
-		if err != nil || failed {
-			return false
-		}
-		return true
-	}
-	// Execute the binary search and hone in on an executable gas limit
-	for lo+1 < hi {
-		mid := (hi + lo) / 2
-		if !executable(mid) {
-			lo = mid
-		} else {
-			hi = mid
+		res, err := b.callContract(ctx, call, b.blockchain.CurrentBlock(), currentState)
+		if err != nil {
+			if errors.Is(err, blockchain.ErrIntrinsicGas) {
+				return true, nil, nil // Special case, raise gas limit
+			}
+			return true, nil, err // Bail out
 		}
+		return res.Failed(), res, nil
 	}
-	// Reject the transaction as invalid if it still fails at the highest allowance
-	if hi == cap {
-		if !executable(hi) {
-			return 0, errGasEstimationFailed
-		}
+
+	estimated, err := blockchain.DoEstimateGas(ctx, call.Gas, 0, call.Value, call.GasPrice, balance, executable)
+	if err != nil {
+		return 0, err
+	} else {
+		return uint64(estimated), nil
 	}
-	return hi, nil
 }
 
 // callContract implements common code between normal and pending contract calls.
 // state is modified during execution, make sure to copy it if necessary.
-func (b *SimulatedBackend) callContract(_ context.Context, call klaytn.CallMsg, block *types.Block, stateDB *state.StateDB) ([]byte, uint64, bool, error) {
+func (b *SimulatedBackend) callContract(_ context.Context, call klaytn.CallMsg, block *types.Block, stateDB *state.StateDB) (*blockchain.ExecutionResult, error) {
 	// Ensure message is initialized properly.
 	if call.GasPrice == nil {
 		call.GasPrice = big.NewInt(1)
@@ -494,15 +468,7 @@ func (b *SimulatedBackend) callContract(_ context.Context, call klaytn.CallMsg,
 	// about the transaction and calling mechanisms.
 	vmenv := vm.NewEVM(evmContext, stateDB, b.config, &vm.Config{})
 
-	ret, usedGas, kerr := blockchain.NewStateTransition(vmenv, msg).TransitionDb()
-
-	// Propagate error of Receipt
-	err := kerr.ErrTxInvalid
-	if err == nil {
-		err = blockchain.GetVMerrFromReceiptStatus(kerr.Status)
-	}
-
-	return ret, usedGas, kerr.Status != types.ReceiptStatusSuccessful, err
+	return blockchain.NewStateTransition(vmenv, msg).TransitionDb()
 }
 
 // SendTransaction updates the pending block to include the given transaction.
@@ -533,7 +499,7 @@ func (b *SimulatedBackend) SendTransaction(_ context.Context, tx *types.Transact
 	stateDB, _ := b.blockchain.State()
 
 	b.pendingBlock = blocks[0]
-	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil)
+	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil, nil)
 	return nil
 }
 
@@ -653,7 +619,7 @@ func (b *SimulatedBackend) AdjustTime(adjustment time.Duration) error {
 	stateDB, _ := b.blockchain.State()
 
 	b.pendingBlock = blocks[0]
-	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil)
+	b.pendingState, _ = state.New(b.pendingBlock.Root(), stateDB.Database(), nil, nil)
 
 	return nil
 }
```

### accounts/abi/bind/backends/simulated_test.go
```diff
@@ -23,7 +23,9 @@ package backends
 import (
 	"bytes"
 	"context"
+	"errors"
 	"math/big"
+	"reflect"
 	"strings"
 	"testing"
 	"time"
@@ -397,25 +399,120 @@ func TestSimulatedBackend_TransactionByHash(t *testing.T) {
 }
 
 func TestSimulatedBackend_EstimateGas(t *testing.T) {
-	sim := NewSimulatedBackend(
-		blockchain.GenesisAlloc{},
-	)
+	/*
+		pragma solidity ^0.6.4;
+		contract GasEstimation {
+		    function PureRevert() public { revert(); }
+		    function Revert() public { revert("revert reason");}
+		    function OOG() public { for (uint i = 0; ; i++) {}}
+		    function Assert() public { assert(false);}
+		    function Valid() public {}
+		}*/
+	const contractAbi = "[{\"inputs\":[],\"name\":\"Assert\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"OOG\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"PureRevert\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"Revert\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"inputs\":[],\"name\":\"Valid\",\"outputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"function\"}]"
+	const contractBin = "0x60806040523480156100115760006000fd5b50610017565b61016e806100266000396000f3fe60806040523480156100115760006000fd5b506004361061005c5760003560e01c806350f6fe3414610062578063aa8b1d301461006c578063b9b046f914610076578063d8b9839114610080578063e09fface1461008a5761005c565b60006000fd5b61006a610094565b005b6100746100ad565b005b61007e6100b5565b005b6100886100c2565b005b610092610135565b005b6000600090505b5b808060010191505061009b565b505b565b60006000fd5b565b600015156100bf57fe5b5b565b6040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252600d8152602001807f72657665727420726561736f6e0000000000000000000000000000000000000081526020015060200191505060405180910390fd5b565b5b56fea2646970667358221220345bbcbb1a5ecf22b53a78eaebf95f8ee0eceff6d10d4b9643495084d2ec934a64736f6c63430006040033"
+
+	key, _ := crypto.GenerateKey()
+	addr := crypto.PubkeyToAddress(key.PublicKey)
+	opts := bind.NewKeyedTransactor(key)
+
+	sim := simTestBackend(addr)
 	defer sim.Close()
-	bgCtx := context.Background()
-	testAddr := crypto.PubkeyToAddress(testKey.PublicKey)
 
-	gas, err := sim.EstimateGas(bgCtx, klaytn.CallMsg{
-		From:  testAddr,
-		To:    &testAddr,
-		Value: big.NewInt(1000),
-		Data:  []byte{},
-	})
-	if err != nil {
-		t.Errorf("could not estimate gas: %v", err)
-	}
+	parsed, _ := abi.JSON(strings.NewReader(contractAbi))
+	contractAddr, _, _, _ := bind.DeployContract(opts, parsed, common.FromHex(contractBin), sim)
+	sim.Commit()
 
-	if gas != params.TxGas {
-		t.Errorf("expected 21000 gas cost for a transaction got %v", gas)
+	cases := []struct {
+		name        string
+		message     klaytn.CallMsg
+		expect      uint64
+		expectError error
+		expectData  interface{}
+	}{
+		{"plain transfer(valid)", klaytn.CallMsg{
+			From:     addr,
+			To:       &addr,
+			Gas:      0,
+			GasPrice: big.NewInt(0),
+			Value:    big.NewInt(1),
+			Data:     nil,
+		}, params.TxGas, nil, nil},
+
+		{"plain transfer(invalid)", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      0,
+			GasPrice: big.NewInt(0),
+			Value:    big.NewInt(1),
+			Data:     nil,
+		}, 0, errors.New("evm: execution reverted"), nil},
+
+		{"Revert", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      0,
+			GasPrice: big.NewInt(0),
+			Value:    nil,
+			Data:     common.Hex2Bytes("d8b98391"),
+		}, 0, errors.New("execution reverted: revert reason"), "0x08c379a00000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000000d72657665727420726561736f6e00000000000000000000000000000000000000"},
+
+		{"PureRevert", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      0,
+			GasPrice: big.NewInt(0),
+			Value:    nil,
+			Data:     common.Hex2Bytes("aa8b1d30"),
+		}, 0, errors.New("evm: execution reverted"), nil},
+
+		{"OOG", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      100000,
+			GasPrice: big.NewInt(0),
+			Value:    nil,
+			Data:     common.Hex2Bytes("50f6fe34"),
+		}, 0, errors.New("gas required exceeds allowance (100000)"), nil},
+
+		{"Assert", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      100000,
+			GasPrice: big.NewInt(0),
+			Value:    nil,
+			Data:     common.Hex2Bytes("b9b046f9"),
+		}, 0, errors.New("VM error occurs while running smart contract"), nil},
+
+		{"Valid", klaytn.CallMsg{
+			From:     addr,
+			To:       &contractAddr,
+			Gas:      100000,
+			GasPrice: big.NewInt(0),
+			Value:    nil,
+			Data:     common.Hex2Bytes("e09fface"),
+		}, 21483, nil, nil},
+	}
+	for _, c := range cases {
+		got, err := sim.EstimateGas(context.Background(), c.message)
+		if c.expectError != nil {
+			if err == nil {
+				t.Fatalf("Expect error, got nil")
+			}
+			if c.expectError.Error() != err.Error() {
+				t.Fatalf("Expect error, want %v, got %v", c.expectError, err)
+			}
+			if c.expectData != nil {
+				if err, ok := err.(*blockchain.RevertError); !ok {
+					t.Fatalf("Expect revert error, got %T", err)
+				} else if !reflect.DeepEqual(err.ErrorData(), c.expectData) {
+					t.Fatalf("Error data mismatch, want %v, got %v", c.expectData, err.ErrorData())
+				}
+			}
+			continue
+		}
+		if got != c.expect {
+			t.Fatalf("Gas estimation mismatch, want %d, got %d", c.expect, got)
+		}
 	}
 }
 
@@ -841,3 +938,116 @@ func TestSimulatedBackend_PendingAndCallContract(t *testing.T) {
 		t.Errorf("response from calling contract was expected to be 'hello world' instead received %v", string(res))
 	}
 }
+
+// This test is based on the following contract:
+/*
+contract Reverter {
+    function revertString() public pure{
+        require(false, "some error");
+    }
+    function revertNoString() public pure {
+        require(false, "");
+    }
+    function revertASM() public pure {
+        assembly {
+            revert(0x0, 0x0)
+        }
+    }
+    function noRevert() public pure {
+        assembly {
+            // Assembles something that looks like require(false, "some error") but is not reverted
+            mstore(0x0, 0x08c379a000000000000000000000000000000000000000000000000000000000)
+            mstore(0x4, 0x0000000000000000000000000000000000000000000000000000000000000020)
+            mstore(0x24, 0x000000000000000000000000000000000000000000000000000000000000000a)
+            mstore(0x44, 0x736f6d65206572726f7200000000000000000000000000000000000000000000)
+            return(0x0, 0x64)
+        }
+    }
+}*/
+var (
+	reverterABI         = `[{"inputs": [],"name": "noRevert","outputs": [],"stateMutability": "pure","type": "function"},{"inputs": [],"name": "revertASM","outputs": [],"stateMutability": "pure","type": "function"},{"inputs": [],"name": "revertNoString","outputs": [],"stateMutability": "pure","type": "function"},{"inputs": [],"name": "revertString","outputs": [],"stateMutability": "pure","type": "function"}]`
+	reverterBin         = "608060405234801561001057600080fd5b506101d3806100206000396000f3fe608060405234801561001057600080fd5b506004361061004c5760003560e01c80634b409e01146100515780639b340e361461005b5780639bd6103714610065578063b7246fc11461006f575b600080fd5b610059610079565b005b6100636100ca565b005b61006d6100cf565b005b610077610145565b005b60006100c8576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526000815260200160200191505060405180910390fd5b565b600080fd5b6000610143576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252600a8152602001807f736f6d65206572726f720000000000000000000000000000000000000000000081525060200191505060405180910390fd5b565b7f08c379a0000000000000000000000000000000000000000000000000000000006000526020600452600a6024527f736f6d65206572726f720000000000000000000000000000000000000000000060445260646000f3fea2646970667358221220cdd8af0609ec4996b7360c7c780bad5c735740c64b1fffc3445aa12d37f07cb164736f6c63430006070033"
+	reverterDeployedBin = "608060405234801561001057600080fd5b506004361061004c5760003560e01c80634b409e01146100515780639b340e361461005b5780639bd6103714610065578063b7246fc11461006f575b600080fd5b610059610079565b005b6100636100ca565b005b61006d6100cf565b005b610077610145565b005b60006100c8576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526000815260200160200191505060405180910390fd5b565b600080fd5b6000610143576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252600a8152602001807f736f6d65206572726f720000000000000000000000000000000000000000000081525060200191505060405180910390fd5b565b7f08c379a0000000000000000000000000000000000000000000000000000000006000526020600452600a6024527f736f6d65206572726f720000000000000000000000000000000000000000000060445260646000f3fea2646970667358221220cdd8af0609ec4996b7360c7c780bad5c735740c64b1fffc3445aa12d37f07cb164736f6c63430006070033"
+)
+
+func TestSimulatedBackend_CallContractRevert(t *testing.T) {
+	testAddr := crypto.PubkeyToAddress(testKey.PublicKey)
+	sim := simTestBackend(testAddr)
+	defer sim.Close()
+	bgCtx := context.Background()
+
+	parsed, err := abi.JSON(strings.NewReader(reverterABI))
+	if err != nil {
+		t.Errorf("could not get code at test addr: %v", err)
+	}
+	contractAuth := bind.NewKeyedTransactor(testKey)
+	addr, _, _, err := bind.DeployContract(contractAuth, parsed, common.FromHex(reverterBin), sim)
+	if err != nil {
+		t.Errorf("could not deploy contract: %v", err)
+	}
+
+	inputs := make(map[string]interface{}, 3)
+	inputs["revertASM"] = nil
+	inputs["revertNoString"] = ""
+	inputs["revertString"] = "some error"
+
+	call := make([]func([]byte) ([]byte, error), 2)
+	call[0] = func(input []byte) ([]byte, error) {
+		return sim.PendingCallContract(bgCtx, klaytn.CallMsg{
+			From: testAddr,
+			To:   &addr,
+			Data: input,
+		})
+	}
+	call[1] = func(input []byte) ([]byte, error) {
+		return sim.CallContract(bgCtx, klaytn.CallMsg{
+			From: testAddr,
+			To:   &addr,
+			Data: input,
+		}, nil)
+	}
+
+	// Run pending calls then commit
+	for _, cl := range call {
+		for key, val := range inputs {
+			input, err := parsed.Pack(key)
+			if err != nil {
+				t.Errorf("could not pack %v function on contract: %v", key, err)
+			}
+
+			res, err := cl(input)
+			if err == nil {
+				t.Errorf("call to %v was not reverted", key)
+			}
+			if res != nil {
+				t.Errorf("result from %v was not nil: %v", key, res)
+			}
+			if val != nil {
+				rerr, ok := err.(*blockchain.RevertError)
+				if !ok {
+					t.Errorf("expect revert error")
+				}
+				if rerr.Error() != "execution reverted: "+val.(string) {
+					t.Errorf("error was malformed: got %v want %v", rerr.Error(), val)
+				}
+			} else {
+				// revert(0x0,0x0)
+				if err.Error() != "evm: execution reverted" {
+					t.Errorf("error was malformed: got %v want %v", err, "evm: execution reverted")
+				}
+			}
+		}
+		input, err := parsed.Pack("noRevert")
+		if err != nil {
+			t.Errorf("could not pack noRevert function on contract: %v", err)
+		}
+		res, err := cl(input)
+		if err != nil {
+			t.Error("call to noRevert was reverted")
+		}
+		if res == nil {
+			t.Errorf("result from noRevert was nil")
+		}
+		sim.Commit()
+	}
+}
```

### accounts/abi/bind/base.go
```diff
@@ -25,6 +25,8 @@ import (
 	"errors"
 	"fmt"
 	"math/big"
+	"strings"
+	"sync"
 
 	"github.com/klaytn/klaytn"
 	"github.com/klaytn/klaytn/accounts/abi"
@@ -76,6 +78,29 @@ type WatchOpts struct {
 	Context context.Context // Network context to support cancellation and timeouts (nil = no timeout)
 }
 
+// MetaData collects all metadata for a bound contract.
+type MetaData struct {
+	mu   sync.Mutex
+	Sigs map[string]string
+	Bin  string
+	ABI  string
+	ab   *abi.ABI
+}
+
+func (m *MetaData) GetAbi() (*abi.ABI, error) {
+	m.mu.Lock()
+	defer m.mu.Unlock()
+	if m.ab != nil {
+		return m.ab, nil
+	}
+	if parsed, err := abi.JSON(strings.NewReader(m.ABI)); err != nil {
+		return nil, err
+	} else {
+		m.ab = &parsed
+	}
+	return m.ab, nil
+}
+
 // BoundContract is the base wrapper object that reflects a contract on the
 // Klaytn network. It contains a collection of methods that are used by the
 // higher level contract bindings to operate.
```

### accounts/abi/bind/template.go
```diff
@@ -55,7 +55,8 @@ type tmplMethod struct {
 	Structured bool       // Whether the returns should be accumulated into a struct
 }
 
-// tmplEvent is a wrapper around an a
+// tmplEvent is a wrapper around an abi.Event that contains a few preprocessed
+// and cached data fields.
 type tmplEvent struct {
 	Original   abi.Event // Original event as parsed by the abi package
 	Normalized abi.Event // Normalized version of the parsed fields
@@ -69,7 +70,7 @@ type tmplField struct {
 	SolKind abi.Type // Raw abi type information
 }
 
-// tmplStruct is a wrapper around an abi.tuple contains an auto-generated
+// tmplStruct is a wrapper around an abi.tuple and contains an auto-generated
 // struct name.
 type tmplStruct struct {
 	Name   string       // Auto-generated struct name(before solidity v0.5.11) or raw name.
@@ -83,8 +84,8 @@ var tmplSource = map[Lang]string{
 	LangJava: tmplSourceJava,
 }
 
-// tmplSourceGo is the Go source template use to generate the contract binding
-// based on.
+// tmplSourceGo is the Go source template that the generated Go contract binding
+// is based on.
 const tmplSourceGo = `
 // Code generated - DO NOT EDIT.
 // This file is a generated binding and any manual changes will be lost.
@@ -94,17 +95,18 @@ package {{.Package}}
 import (
 	"math/big"
 	"strings"
+	"errors"
 
 	"github.com/klaytn/klaytn"
 	"github.com/klaytn/klaytn/accounts/abi/bind"
-	"github.com/klaytn/klaytn/accounts/abi"
 	"github.com/klaytn/klaytn/common"
 	"github.com/klaytn/klaytn/blockchain/types"
 	"github.com/klaytn/klaytn/event"
 )
 
 // Reference imports to suppress errors if they are not otherwise used.
 var (
+	_ = errors.New
 	_ = big.NewInt
 	_ = strings.NewReader
 	_ = klaytn.NotFound
@@ -124,35 +126,51 @@ var (
 {{end}}
 
 {{range $contract := .Contracts}}
+	// {{.Type}}MetaData contains all meta data concerning the {{.Type}} contract.
+	var {{.Type}}MetaData = &bind.MetaData{
+		ABI: "{{.InputABI}}",
+		{{if $contract.FuncSigs -}}
+		Sigs: map[string]string{
+			{{range $strsig, $binsig := .FuncSigs}}"{{$binsig}}": "{{$strsig}}",
+			{{end}}
+		},
+		{{end -}}
+		{{if .InputBin -}}
+		Bin: "0x{{.InputBin}}",
+		{{end}}
+	}
 	// {{.Type}}ABI is the input ABI used to generate the binding from.
-	const {{.Type}}ABI = "{{.InputABI}}"
+	// Deprecated: Use {{.Type}}MetaData.ABI instead.
+	var {{.Type}}ABI = {{.Type}}MetaData.ABI
 
     // {{.Type}}BinRuntime is the compiled bytecode used for adding genesis block without deploying code.
     const {{.Type}}BinRuntime = ` + "`" + `{{.InputBinRuntime}}` + "`" + `
 
 	{{if $contract.FuncSigs}}
 		// {{.Type}}FuncSigs maps the 4-byte function signature to its string representation.
-		var {{.Type}}FuncSigs = map[string]string{
-			{{range $strsig, $binsig := .FuncSigs}}"{{$binsig}}": "{{$strsig}}",
-			{{end}}
-		}
+		// Deprecated: Use {{.Type}}MetaData.Sigs instead.
+		var {{.Type}}FuncSigs = {{.Type}}MetaData.Sigs
 	{{end}}
 
 	{{if .InputBin}}
 		// {{.Type}}Bin is the compiled bytecode used for deploying new contracts.
-		var {{.Type}}Bin = "0x{{.InputBin}}"
+		// Deprecated: Use {{.Type}}MetaData.Bin instead.
+		var {{.Type}}Bin = {{.Type}}MetaData.Bin
 
 		// Deploy{{.Type}} deploys a new Klaytn contract, binding an instance of {{.Type}} to it.
 		func Deploy{{.Type}}(auth *bind.TransactOpts, backend bind.ContractBackend {{range .Constructor.Inputs}}, {{.Name}} {{bindtype .Type $structs}}{{end}}) (common.Address, *types.Transaction, *{{.Type}}, error) {
-		  parsed, err := abi.JSON(strings.NewReader({{.Type}}ABI))
+		  parsed, err := {{.Type}}MetaData.GetAbi()
 		  if err != nil {
 		    return common.Address{}, nil, nil, err
 		  }
+		  if parsed == nil {
+			return common.Address{}, nil, nil, errors.New("GetABI returned nil")
+		  }
 		  {{range $pattern, $name := .Libraries}}
 			{{decapitalise $name}}Addr, _, _, _ := Deploy{{capitalise $name}}(auth, backend)
 			{{$contract.Type}}Bin = strings.Replace({{$contract.Type}}Bin, "__${{$pattern}}$__", {{decapitalise $name}}Addr.String()[2:], -1)
 		  {{end}}
-		  address, tx, contract, err := bind.DeployContract(auth, parsed, common.FromHex({{.Type}}Bin), backend {{range .Constructor.Inputs}}, {{.Name}}{{end}})
+		  address, tx, contract, err := bind.DeployContract(auth, *parsed, common.FromHex({{.Type}}Bin), backend {{range .Constructor.Inputs}}, {{.Name}}{{end}})
 		  if err != nil {
 		    return common.Address{}, nil, nil, err
 		  }
@@ -257,11 +275,11 @@ var (
 
 	// bind{{.Type}} binds a generic wrapper to an already deployed contract.
 	func bind{{.Type}}(address common.Address, caller bind.ContractCaller, transactor bind.ContractTransactor, filterer bind.ContractFilterer) (*bind.BoundContract, error) {
-	  parsed, err := abi.JSON(strings.NewReader({{.Type}}ABI))
+	  parsed, err := {{.Type}}MetaData.GetAbi()
 	  if err != nil {
 	    return nil, err
 	  }
-	  return bind.NewBoundContract(address, parsed, caller, transactor, filterer), nil
+	  return bind.NewBoundContract(address, *parsed, caller, transactor, filterer), nil
 	}
 
 	// Call invokes the (constant) contract method with params as input values and
@@ -551,8 +569,8 @@ var (
 {{end}}
 `
 
-// tmplSourceJava is the Java source template use to generate the contract binding
-// based on.
+// tmplSourceJava is the Java source template that the generated Java contract binding
+// is based on.
 const tmplSourceJava = `
 // This file is an automatically generated Java binding. Do not modify as any
 // change will likely be lost upon the next re-generation!
```

# [?] Merge remote-tracking branch 'origin/develop' into feature/vertex-store-overflow-mitigations

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2025-02-17
Source: https://github.com/radixdlt/babylon-node/commit/5a95313bacefcd0ba5d49cf6c07f018756bc3fec
Type: security-commit

## Details
Merge remote-tracking branch 'origin/develop' into feature/vertex-store-overflow-mitigations

## Patch
### .dockerignore
```diff
@@ -4,6 +4,7 @@
 
 # Radix non-versioned files
 /**/RADIXDB/
+/**/RADIXDB_OLD/
 /**/NODEMOUNT/
 /**/RADIXDB_TEST/
 /**/logs/
@@ -56,9 +57,10 @@
 /**/*.swo
 /**/*.swp
 /**/*~
-# ignore jar files, but keep Gradle wrapper
+# ignore jar files, but keep Gradle wrapper and build artifacts
 /**/*.jar
 !gradle/wrapper/gradle-wrapper.jar
+!artifacts/*.jar
 
 # node
 /**/node_modules/
```

### .github/CODEOWNERS
```diff
@@ -0,0 +1,20 @@
+# Docs:
+# - https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
+
+# Ideally, we want the following rules:
+# - Each normal code review requires an approval from the protocol team
+# - Each change to something security-sensitive (lock file or .github folder) requires an approval from the security subteam
+# - Each workflow change requires a devops approval
+#
+# However, there isn't a way for a single file change to require two sets of approvals,
+# ... so we ignore devops here, and make it just require a protocol-security-approvers
+
+# DEFAULT
+* @radixdlt/protocol-github-approvers
+
+# SECURITY-SENSITIVE
+/.github/ @radixdlt/protocol-security-approvers
+*.lock @radixdlt/protocol-security-approvers
+
+# API INTERFACES
+*api-schema.yaml @radixdlt/interfaces-github-approvers
```

### .github/actions/setup-env/action.yml
```diff
@@ -0,0 +1,40 @@
+name: 'Setup build environment'
+description: 'Common GH action to setup job environment'
+inputs:
+  cross-compile-to-windows:
+    description: "If 'true' then do some additional build environment setup"
+    required: false
+    default: "false" # or "true"
+
+runs:
+  using: "composite"
+  steps:
+    - name: Install Rust toolchain
+      uses: RDXWorks-actions/toolchain@master
+      with:
+        # IMPORTANT: This version should match the version in radixdlt-scrypto on respective branch
+        toolchain: 1.81.0
+        default: true
+        target: ${{inputs.cross-compile-to-windows == 'true' && 'x86_64-pc-windows-msvc' || ''}}
+
+    - name: Set up JDK 17
+      if: ${{ inputs.cross-compile-to-windows == 'false' }}
+      uses: RDXWorks-actions/setup-java@main
+      with:
+        distribution: 'zulu'
+        java-version: '17'
+
+    - name: Install libclang-dev
+      if: ${{ inputs.cross-compile-to-windows == 'false' }}
+      run: sudo apt-get update -y && sudo apt-get install -y libclang-dev
+      shell: bash
+
+    ## Steps for cross-compilation to Windows
+    - name: Update clang version to 17
+      if: ${{ inputs.cross-compile-to-windows == 'true' }}
+      run: sudo apt remove clang-14 && sudo apt autoclean && sudo apt autoremove && wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && sudo ./llvm.sh 17 && sudo ls /usr/bin/ | grep clang && sudo ln -sf /usr/bin/clang-17 /usr/bin/clang && sudo ln -sf /usr/bin/clang++-17 /usr/bin/clang++ && sudo apt-get install -y libclang-dev llvm llvm-dev
+      shell: bash
+    - name: Install cargo-xwin
+      if: ${{ inputs.cross-compile-to-windows == 'true' }}
+      run: cargo install cargo-xwin --version 0.17.1 --locked
+      shell: bash
```

### .github/pull_request_template.md
```diff
@@ -1,29 +1,43 @@
 > [!IMPORTANT]
 >
-> * Please read our [Contributing Guidelines](https://github.com/radixdlt/babylon-node/blob/main/CONTRIBUTING.md) before opening a PR.
-> * Before creating your PR, please ensure you have used the _correct base branch_ as per the [branching strategy](https://github.com/radixdlt/babylon-node/blob/main/docs/branching-strategy.md), both for branching from, and in the PR UI above.
->   * For most code changes, this is `develop`.
->   * For stand-alone docs changes, this is `main`.
->   * For workflow changes, this is the oldest supported `release/*` branch. 
-> * Please remove these sections as you fill out your PR.
+> * Please read our [Contributing Guidelines](/CONTRIBUTING.md) before opening a PR.
+> * Before creating your PR, please ensure you read the [branching strategy](/docs/branching-strategy.md). The end result after completing the merge actions should be that `release/XXX <= develop`, where `XXX` is the latest released protocol version. This ensures that we minimise merge conflicts, and that work doesn't go missing.
+> * As per the branching strategy, **you must ensure you select the _correct base branch_**, both for branching from, and in the PR UI above. The following process can be used to decide the base branch:
+>   * For README changes or code changes which can wait until the next protocol update to be released, use `develop`. This should be the default for code changes.
+>   * For github workflow changes, or code changes which need to go out as a fully-interoperable update to the node at the current protocol version, use `release/XXX`.
+>     * Such changes must be tested and reviewed more carefully to mitigate the risk of regression.
+>     * Once the change is merged, it is the merger's responsibility to ensure `release/XXX` is merged into the `develop` branch.
 > 
+> _Please remove this section once you confirm you follow its guidance._
 
 ## Summary
 
+<!--
 > [!TIP]
 > 
 > Start with the context of your PR. Why are you making this change? What does it address? Link back to an issue if relevant.
 > 
-> Then summarise the changes that were made. Bullet points are fine.
+> Then summarise the changes that were made.
+> * Bullet points are fine.
+> * Feel free to add additional subheadings (using ###) with more information if required.
+-->
 
-## Details
+## Testing
 
+<!--
 > [!TIP]
 > 
-> This section is optional. Go into more detail about the changes that were made, or the thinking behind the changes.
+> Explain what testing / verification is done, including manual testing or automated testing.
+-->
 
-## Testing
+## Changelog
 
+<!--
 > [!TIP]
-> 
-> Explain what testing / verification is done, including manual testing or automated testing.
+>
+> If the change in your PR is a new feature, or could affect or break any API integrators, then it likely will need an update to the CHANGELOG.md file.
+>
+> After making any required updates, write either of these two:
+> * "The changelog has been updated to capture XX changes which affect XX"
+> * "The changelog was not updated because this change has no user-facing impact"
+-->
\ No newline at end of file
```

### .github/workflows/add-artifacts-to-release.yml
```diff
@@ -7,7 +7,7 @@ on:
 jobs:
   setup_version_properties:
     name: Setup version properties
-    runs-on: ubuntu-latest
+    runs-on: ubuntu-22.04
     outputs:
       VERSION_BRANCH: ${{ steps.setup_version_properties.outputs.VERSION_BRANCH }}
       VERSION_BUILD: ${{ steps.setup_version_properties.outputs.VERSION_BUILD }}
@@ -37,11 +37,13 @@ jobs:
             target: aarch64-apple-darwin
             artifact: 'libcorerust.dylib'
             zipname: 'arch-darwin-aarch64'
-          - os: ubuntu-latest
+            # We use ubuntu-22.04 rather than ubuntu-latest to get a fixed GLIBC dependency
+            # We can update this when we update our minimum supported linux version
+          - os: ubuntu-22.04 # Fix GLIBC
             target: x86_64-unknown-linux-gnu
             artifact: 'libcorerust.so'
             zipname: 'arch-linux-x86_64'
-          - os: ubuntu-latest
+          - os: ubuntu-22.04 # Fix GLIBC
             target: aarch64-unknown-linux-gnu
             zipname: 'arch-linux-aarch64'
             artifact: 'libcorerust.so'
@@ -86,15 +88,15 @@ jobs:
         run: |
           rustup toolchain install stable-gnu
           rustup set default-host ${{ matrix.target }}
-      - if: matrix.os == 'ubuntu-latest'
+      - if: matrix.os == 'ubuntu-22.04' # Fix GLIBC
         name: Build dependencies ubuntu
         run: |
           sudo apt-get update -y && sudo apt install -y gcc-aarch64-linux-gnu g++-aarch64-linux-gnu
           # sudo apt install -y gcc-i686-linux-gnu g++-i686-linux-gnu
       - name: Build core-rust
         run: |
           cd core-rust
-          cargo build --release --profile=release --target ${{ matrix.target }}
+          cargo build --release --target ${{ matrix.target }}
           echo "ls  ./target/${{ matrix.target }}/release"
           ls  ./target/${{ matrix.target }}/release/
         env:
@@ -112,7 +114,7 @@ jobs:
       - setup_version_properties
     permissions:
       contents: write
-    runs-on: 'ubuntu-latest'
+    runs-on: 'ubuntu-22.04' # Fix GLIBC
     continue-on-error: true
     strategy:
       matrix:
@@ -160,7 +162,7 @@ jobs:
     name: Build and Upload Application Binary
     permissions:
       contents: write
-    runs-on: ubuntu-22.04
+    runs-on: ubuntu-22.04 # Fix GLIBC
     needs:
       - setup_version_properties
     environment: publish-artifacts
@@ -203,7 +205,7 @@ jobs:
   snyk-sbom:
     if: github.event_name == 'release'
     name: SBOM
-    runs-on: ubuntu-latest
+    runs-on: ubuntu-22.04 # Fix GLIBC
     permissions: write-all
     steps:
       - uses: RDXWorks-actions/checkout@main
```

### .github/workflows/ci.yml
```diff
@@ -6,13 +6,30 @@ concurrency:
 
 on:
   pull_request:
-    # Runs on all PRs
+# Runs on all PRs
   push:
     branches:
       - develop
       - main
       - release\/*
 jobs:
+  phylum-analyze:
+    if: ${{ github.event.pull_request }}
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/phylum-analyze.yml@main
+    permissions:
+      id-token: write
+      pull-requests: write
+      contents: read
+      deployments: write
+    secrets:
+      phylum_api_key: ${{ secrets.PHYLUM_API_KEY }}
+    with:
+      phylum_pr_number: ${{ github.event.number }}
+      phylum_pr_name: ${{ github.head_ref }}
+      phylum_group_name: Protocol
+      phylum_project_id: 3f5b2c53-46bd-4f68-b050-5898f929002f
+      github_repository: ${{ github.repository }}
+      add_report_comment_to_pull_request: true
   snyk-scan-deps-licences:
     name: Snyk deps/licences scan
     runs-on: ubuntu-latest
@@ -31,6 +48,8 @@ jobs:
           secret_prefix: 'SNYK'
           secret_name: ${{ secrets.AWS_SECRET_NAME_SNYK }}
           parse_json: true
+      - name: Create .snyk file
+        run: echo "${{ vars.DOT_SNYK_FILE }}" > .snyk
       - name: Run Snyk to check for deps vulnerabilities
         uses: RDXWorks-actions/snyk-actions/gradle-jdk17@master
         with:
@@ -53,8 +72,11 @@ jobs:
           secret_prefix: 'SNYK'
           secret_name: ${{ secrets.AWS_SECRET_NAME_SNYK }}
           parse_json: true
+      - name: Create .snyk file
+        run: echo "${{ vars.DOT_SNYK_FILE }}" > .snyk
       - name: Run Snyk to check for code vulnerabilities
         uses: RDXWorks-actions/snyk-actions/gradle-jdk17@master
+        continue-on-error: true
         with:
           args: --all-projects --org=${{ env.SNYK_NETWORK_ORG_ID }} --severity-threshold=high
           command: code test
@@ -92,17 +114,8 @@ jobs:
         with:
           # Shallow clones should be disabled for a better relevancy of analysis
           fetch-depth: 0
-      - uses: RDXWorks-actions/rust-toolchain@master
-        with:
-          toolchain: 1.77.2
-          default: true
-      - name: Set up JDK 17
-        uses: RDXWorks-actions/setup-java@main
-        with:
-          distribution: 'zulu'
-          java-version: '17'
-      - name: Install libclang-dev
-        run: sudo apt-get update -y && sudo apt-get install -y libclang-dev
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
       - name: Cache SonarCloud packages
         uses: RDXWorks-actions/cache@main
         with:
@@ -151,7 +164,7 @@ jobs:
           name: distZip
           retention-days: 7
       - uses: ./.github/actions/fetch-secrets
-        with: 
+        with:
           role_name: "${{ secrets.COMMON_SECRETS_ROLE_ARN }}"
           app_name: "babylon-node"
           step_name: "build"
@@ -172,15 +185,8 @@ jobs:
         with:
           # Shallow clones should be disabled for a better relevancy of analysis
           fetch-depth: 0
-      - uses: RDXWorks-actions/rust-toolchain@master
-        with:
-          toolchain: 1.77.2
-          default: true
-      - name: Set up JDK 17
-        uses: RDXWorks-actions/setup-java@main
-        with:
-          distribution: 'zulu'
-          java-version: '17'
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
       - name: Cache Gradle packages
         uses: RDXWorks-actions/cache@main
         with:
@@ -197,17 +203,8 @@ jobs:
         with:
           # Shallow clones should be disabled for a better relevancy of analysis
           fetch-depth: 0
-      - uses: RDXWorks-actions/rust-toolchain@master
-        with:
-          toolchain: 1.77.2
-          default: true
-      - name: Set up JDK 17
-        uses: RDXWorks-actions/setup-java@main
-        with:
-          distribution: 'zulu'
-          java-version: '17'
-      - name: Install libclang-dev
-        run: sudo apt-get update -y && sudo apt-get install -y libclang-dev
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
       - name: Cache Gradle packages
         uses: RDXWorks-actions/cache@main
         with:
@@ -216,7 +213,8 @@ jobs:
           restore-keys: ${{ runner.os }}-gradle
       - name: Run steady-state integration tests
         env:
-          RADIXDLT_LOG_LEVEL: warn
+          # Might be set to warn for debugging purposes. Warning, log file will be huge.
+          RADIXDLT_LOG_LEVEL: error
         run: ./gradlew clean runSteadyStateIntegrationTests --info --refresh-dependencies
   targeted-integration:
     name: Targeted integration tests
@@ -226,17 +224,8 @@ jobs:
         with:
           # Shallow clones should be disabled for a better relevancy of analysis
           fetch-depth: 0
-      - uses: RDXWorks-actions/rust-toolchain@master
-        with:
-          toolchain: 1.77.2
-          default: true
-      - name: Set up JDK 17
-        uses: RDXWorks-actions/setup-java@main
-        with:
-          distribution: 'zulu'
-          java-version: '17'
-      - name: Install libclang-dev
-        run: sudo apt-get update -y && sudo apt-get install -y libclang-dev
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
       - name: Cache Gradle packages
         uses: RDXWorks-actions/cache@main
         with:
@@ -245,24 +234,55 @@ jobs:
           restore-keys: ${{ runner.os }}-gradle
       - name: Run targeted integration tests
         env:
-          RADIXDLT_LOG_LEVEL: warn
+          # Might be set to warn for debugging purposes. Warning, log file will be huge.
+          RADIXDLT_LOG_LEVEL: error
         run: ./gradlew clean runTargetedIntegrationTests --info --refresh-dependencies --parallel
+  mesh-api-test-suite:
+    name: Run Mesh API tests
+    runs-on: selfhosted-ubuntu-22.04-16-cores
+    steps:
+      - uses: RDXWorks-actions/checkout@main
+        with:
+          # Shallow clones should be disabled for a better relevancy of analysis
+          fetch-depth: 0
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
+      - name: Cache Gradle packages
+        uses: RDXWorks-actions/cache@main
+        with:
+          path: ~/.gradle/caches
+          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle') }}
+          restore-keys: ${{ runner.os }}-gradle
+      - name: Build Node
+        run: ./gradlew build
+      - name: Run Node in the background
+        env:
+          # This is to skip keygen step
+          RADIXDLT_NODE_KEY: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY=
+        run: |
+          echo "db.historical_substate_values.enable=true" >> core/default.config
+          ./gradlew :core:run --info &
+      - name: Wait for 2 minutes
+        run: sleep 2m
+      - name: Install mesh-cli
+        run: curl -sSfL https://raw.githubusercontent.com/coinbase/mesh-cli/master/scripts/install.sh | sh -s
+      - name: Run Data API tests
+        run: ./bin/rosetta-cli --configuration-file core-rust/mesh-api-server/mesh-cli-configs/localnet.json check:data
+      - name: Run Construction API tests
+        run: ./bin/rosetta-cli --configuration-file core-rust/mesh-api-server/mesh-cli-configs/localnet.json check:construction
+      - name: Run Coinbase-spec tests
+        run: ./bin/rosetta-cli --configuration-file core-rust/mesh-api-server/mesh-cli-configs/localnet.json check:spec
   cross-xwin:
     name: Cross compile to Windows
     runs-on: ubuntu-latest
     steps:
       - uses: RDXWorks-actions/checkout@main
         with:
           fetch-depth: 1
-      - uses: RDXWorks-actions/rust-toolchain@master
+      - name: Setup environment
+        uses: ./.github/actions/setup-env
         with:
-          toolchain: 1.77.2
-          default: true
-          targets: x86_64-pc-windows-msvc
-      - name: Update clang version to 17
-        run: sudo apt remove clang-14 && sudo apt autoclean && sudo apt autoremove && wget https://apt.llvm.org/llvm.sh && chmod +x llvm.sh && sudo ./llvm.sh 17 && sudo ls /usr/bin/ | grep clang && sudo ln -sf /usr/bin/clang-17 /usr/bin/clang && sudo ln -sf /usr/bin/clang++-17 /usr/bin/clang++ && sudo apt-get install -y libclang-dev llvm llvm-dev
-      - name: Install cargo-xwin
-        run: cargo install cargo-xwin
+          cross-compile-to-windows: "true"
       - name: cross compile to windows
         run: pushd core-rust; cargo xwin build --release --target x86_64-pc-windows-msvc
       - name: Publish corerust.dll
```

### .github/workflows/docker.yml
```diff
@@ -10,16 +10,11 @@ on:
       - main
       - release\/*
 
-jobs:
-  cancel_running_workflows:
-    name: Cancel running workflows
-    runs-on: ubuntu-22.04
-    steps:
-      - name: cancel running workflows
-        uses: RDXWorks-actions/cancel-workflow-action@main
-        with:
-          access_token: ${{ github.token }}
+concurrency:
+  group: ${{ github.workflow }}-${{ github.ref }}
+  cancel-in-progress: true
 
+jobs:
   build_deb:
     name: Build debian package
     runs-on: selfhosted-ubuntu-22.04-16-cores
@@ -140,7 +135,7 @@ jobs:
       packages: write
     uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
     with:
-      runs_on: ubuntu-latest
+      runs_on: ubuntu-16-cores-selfhosted
       image_registry: "docker.io"
       image_organization: "radixdlt"
       image_name: "private-babylon-node"
@@ -229,7 +224,7 @@ jobs:
       pull-requests: read
     uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/join-docker-images-all-tags.yml@main
     with:
-      aws_dockerhub_secret: github-actions/common/dockerhub-credentials
+      aws_dockerhub_secret: github-actions/common/dockerhub-credentials-read-only
       amd_meta_data_json: ${{needs.build_push_container_private.outputs.json}}
     secrets:
       role-to-assume: "arn:aws:iam::308190735829:role/gh-common-secrets-read-access"
@@ -246,7 +241,7 @@ jobs:
       packages: write
     uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
     with:
-      runs_on: ubuntu-latest
+      runs_on: ubuntu-16-cores-selfhosted
       image_registry: "docker.io"
       image_organization: "radixdlt"
       image_name: "babylon-node"
@@ -372,32 +367,48 @@ jobs:
           args: --all-projects --org=${{ env.SNYK_NETWORK_ORG_ID }} --target-reference=${{ github.ref_name }}
           command: monitor
 
-# TEMPORARILY REMOVE EPHEMERAL TESTS
-# => Until we can change them to only run the "node" tests and not the transaction tests
-# ephemeral-deploy-and-test:
-#   name: Run ephemeral deploy and test
-#   needs:
-#     - build_deb
-#     - build_push_container
-#   runs-on: ubuntu-22.04
-#   steps:
-#     - name: Get docker image tag
-#       run: |
-#         #There can be multiple tag entries. Get the first and only take the tag (i.e. not the image repo and name)
-#         TAGS="${{ needs.build_deb.outputs.tags }}"
-#         DOCKER_TAG=$(echo $TAGS | awk 'NR==1{print $1}' | cut -d':' -f2)
-#         echo "DOCKER_TAG=$DOCKER_TAG" >> $GITHUB_ENV
-#         echo "BABYLON_NODE_BRANCH=$GITHUB_HEAD_REF" >> $GITHUB_ENV
-#     - name: Deploy and test on ephemeral network
-#       uses: RDXWorks-actions/jenkins-job-trigger-action@master
-#       with:
-#         jenkins_url: "${{ env.JENKINS_URL }}"
-#         jenkins_user: ${{ env.JENKINS_USER }}
-#         jenkins_token: ${{ env.JENKINS_TOKEN }}
-#         job_name: "ephemeral-deployments/job/ephemeral-env-deploy-and-test"
-#         job_params: |
-#           {
-#             "nodeDockerTag": "${{ env.DOCKER_TAG }}",
-#             "babylonNodeBranch": "${{ env.BABYLON_NODE_BRANCH }}"
-#           }
-#         job_timeout: "3600"
+  ephemeral-deploy-and-benchmark:
+    permissions:
+      id-token: write
+      contents: read
+    name: Deploy ephemeral environment and run benchmark tests.
+    needs:
+      - setup_tags
+      - build_push_container_private
+    runs-on: ubuntu-22.04
+    steps:
+      - uses: RDXWorks-actions/checkout@main
+        with:
+          # Shallow clones should be disabled for a better relevancy of analysis
+          fetch-depth: 0
+      - uses: ./.github/actions/fetch-secrets
+        with:
+          role_name: "${{ secrets.BABYLON_SECRETS_ROLE_ARN }}"
+          app_name: "babylon-node"
+          step_name: "deploy"
+          secret_prefix: "JENKINS"
+          secret_name: "github-actions/radixdlt/babylon-node/jenkins-api-token"
+          parse_json: true
+      - name: Connect to tailnet
+        uses: radixdlt/public-iac-resuable-artifacts/tailnet@main
+        with:
+          role_name: "arn:aws:iam::${{ secrets.SECRETS_ACCOUNT_ID }}:role/gh-common-secrets-read-access"
+          region: "eu-west-2"
+          secret_name: "arn:aws:secretsmanager:eu-west-2:${{ secrets.SECRETS_ACCOUNT_ID }}:secret:github-actions/common/tailscale-public-workflows-DpiE80"
+      - name: Get docker image tag
+        run: |
+          echo "GITHUB_REF_NAME=$GITHUB_REF_NAME" >> $GITHUB_ENV
+          echo "GITHUB_REPOSITORY=$GITHUB_REPOSITORY" >> $GITHUB_ENV
+      - name: Deploy and test on ephemeral network
+        uses: RDXWorks-actions/jenkins-job-trigger-action@master
+        with:
+          jenkins_url: "${{ env.JENKINS_URL }}"
+          jenkins_user: ${{ env.JENKINS_USER }}
+          jenkins_token: ${{ env.JENKINS_TOKEN }}
+          job_name: "babylon-testing/job/ephemeral-deployments/job/ephemeral-node-ci-benchmark"
+          job_params: |
+            {
+              "RADIXDLT_NODE_DOCKER_TAG": "${{ needs.setup_tags.outputs.tag }}",
+              "RADIXDLT_GITHUB_TRIGGER" : "${{ env.GITHUB_REPOSITORY }}:${{ env.GITHUB_REF_NAME }}"
+            }
+          job_timeout: "3600"
```

### .github/workflows/phylum-daily-analysis.yaml
```diff
@@ -0,0 +1,65 @@
+name: Daily Analysis Phylum
+
+on:
+  schedule:
+    # Runs at 14:00 UTC every day
+    - cron: '0 13 * * *'
+
+env:
+  PHYLUM_PROJECT_ID: 3f5b2c53-46bd-4f68-b050-5898f929002f
+  PHYLUM_GROUP_NAME: Protocol
+  PHYLUM_NAME: babylon-node
+jobs:
+  analyze_branch_phylum:
+    name: Analyze dependencies with Phylum
+    permissions:
+      contents: read
+      pull-requests: write
+    runs-on: ubuntu-latest
+    strategy:
+      matrix:
+        branch: [main, develop, release/babylon, release/anemone, release/bottlenose]
+        include:
+          - branch: main
+          - branch: develop
+          - branch: release/babylon
+          - branch: release/anemone
+          - branch: release/bottlenose
+      fail-fast: false 
+    steps:
+      - uses: RDXWorks-actions/checkout@main
+        with:
+          ref: ${{ matrix.branch }}
+          fetch-depth: 0
+      - uses: RDXWorks-actions/setup-python@main
+        with:
+          python-version: 3.10.6
+      - name: Install Phylum
+        run: |
+          curl https://sh.phylum.io/ | sh -s -- --yes
+          # Add the Python user base binary directory to PATH
+          echo "$HOME/.local/bin" >> $GITHUB_PATH
+      - name: Run Phylum Analysis
+        env: 
+          PHYLUM_API_KEY: ${{ secrets.PHYLUM_API_KEY }}         
+        run: | 
+          phylum analyze --quiet --label ${{ matrix.branch }}_branch_daily_schedule > /dev/null 2>&1 || exit_code=$?
+          if [ $exit_code -eq 100 ]; then 
+            echo "Phylum Analysis returned exit code 100, but continuing.";
+            echo "phylum_analyze_status=failure" >> $GITHUB_ENV 
+            exit 0; 
+          else 
+            echo "phylum_analyze_status=success" >> $GITHUB_ENV 
+            exit $?; 
+          fi
+      - name: Analysis Status Failure notification
+        if: always()
+        uses: RDXWorks-actions/notify-slack-action@master
+        with:
+          status: ${{ env.phylum_analyze_status }}
+          notify_when: 'failure'
+          notification_title: ':clock3: Phylum Scheduled Daily Analysis:'
+          message_format: 'Automatic phylum analysis has found vulnerabilities on ${{ env.PHYLUM_NAME }} in ${{ matrix.branch }} branch:boom:'
+          footer: "Linked Repository <{repo_url}|{repo}> | <https://app.phylum.io/projects/${{ env.PHYLUM_PROJECT_ID }}?label=${{ matrix.branch }}_branch_daily_schedule&group=${{ env.PHYLUM_GROUP_NAME }}|View Report> "
+        env:
+          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_PHYLUM_PROTOCOL_TEAM_WEBHOOK }}
\ No newline at end of file
```

### .github/workflows/publish-build-layer-images.yml
```diff
@@ -0,0 +1,206 @@
+name: Publish build layer images
+
+on:
+  workflow_dispatch:
+    inputs:
+      docker_tag:
+        description: "Docker tag to be published"
+
+permissions:
+  packages: write
+  pull-requests: write
+  id-token: write
+  contents: read
+
+jobs:
+  build_rust_amd64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: ubuntu-16-cores-selfhosted
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-rust
+      context: "."
+      dockerfile: docker/base-images/rust-builder.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/amd64"
+      provenance: "false"
+      scan_image: true
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: amd64
+      flavor: |
+        suffix=-amd64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  build_rust_arm64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: selfhosted-ubuntu-22.04-arm
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-rust
+      context: "."
+      dockerfile: docker/base-images/rust-builder.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/arm64"
+      provenance: "false"
+      scan_image: false
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: arm64
+      flavor: |
+        suffix=-arm64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  join_rust_multiarch_image:
+    name: Join multiarch image
+    needs:
+      - build_rust_amd64
+      - build_rust_arm64
+    permissions:
+      id-token: write
+      contents: read
+      pull-requests: read
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/join-docker-images-all-tags.yml@main
+    with:
+      aws_dockerhub_secret: github-actions/rdxworks/dockerhub-images/release-credentials
+      amd_meta_data_json: ${{needs.build_rust_amd64.outputs.json}}
+    secrets:
+      role-to-assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  build_java_amd64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: ubuntu-16-cores-selfhosted
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-java
+      context: "."
+      dockerfile: docker/base-images/java-builder.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/amd64"
+      provenance: "false"
+      scan_image: true
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: amd64
+      flavor: |
+        suffix=-amd64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  build_java_arm64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: selfhosted-ubuntu-22.04-arm
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-java
+      context: "."
+      dockerfile: docker/base-images/java-builder.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/arm64"
+      provenance: "false"
+      scan_image: false
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: arm64
+      flavor: |
+        suffix=-arm64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  join_java_multiarch_image:
+    name: Join multiarch image
+    needs:
+      - build_java_amd64
+      - build_java_arm64
+    permissions:
+      id-token: write
+      contents: read
+      pull-requests: read
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/join-docker-images-all-tags.yml@main
+    with:
+      aws_dockerhub_secret: github-actions/rdxworks/dockerhub-images/release-credentials
+      amd_meta_data_json: ${{needs.build_java_amd64.outputs.json}}
+    secrets:
+      role-to-assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  build_app_amd64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: ubuntu-16-cores-selfhosted
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-app
+      context: "."
+      dockerfile: docker/base-images/app.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/amd64"
+      provenance: "false"
+      scan_image: true
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: amd64
+      flavor: |
+        suffix=-amd64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  build_app_arm64:
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/docker-build.yml@main
+    with:
+      runs_on: selfhosted-ubuntu-22.04-arm
+      environment: "release"
+      image_registry: "docker.io"
+      image_organization: "radixdlt"
+      image_name: "babylon-node-build-layers"
+      tag: ${{ inputs.docker_tag }}-app
+      context: "."
+      dockerfile: docker/base-images/app.dockerfile
+      target: "babylon-node-build-layers"
+      platforms: "linux/arm64"
+      provenance: "false"
+      scan_image: false
+      snyk_target_ref: ${{ github.ref_name }}
+      enable_dockerhub: true
+      use_gh_remote_cache: true
+      cache_tag_suffix: arm64
+      flavor: |
+        suffix=-arm64
+    secrets:
+      role_to_assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
+
+  join_app_multiarch_image:
+    name: Join multiarch image
+    needs:
+      - build_app_amd64
+      - build_app_arm64
+    permissions:
+      id-token: write
+      contents: read
+      pull-requests: read
+    uses: radixdlt/public-iac-resuable-artifacts/.github/workflows/join-docker-images-all-tags.yml@main
+    with:
+      aws_dockerhub_secret: github-actions/rdxworks/dockerhub-images/release-credentials
+      amd_meta_data_json: ${{needs.build_app_amd64.outputs.json}}
+    secrets:
+      role-to-assume: ${{ secrets.DOCKERHUB_RELEASER_ROLE }}
```

### .gitignore
```diff
@@ -48,6 +48,7 @@ api.users
 
 # radixdlt non-versioned files
 RADIXDB/
+RADIXDB_OLD/
 NODEMOUNT/
 RADIXDB_TEST/
 logs/
@@ -67,4 +68,7 @@ node_modules/
 **/resources/markdown
 
 # code coverage info
-**/lcov.info
\ No newline at end of file
+**/lcov.info
+
+# CI generated
+artifacts
```

### .phylum_project
```diff
@@ -0,0 +1,9 @@
+id: 3f5b2c53-46bd-4f68-b050-5898f929002f
+name: babylon-node
+created_at: 2024-07-05T10:48:15.419011+02:00
+group_name: Protocol
+depfiles:
+  - path: ./core/gradle.lockfile
+    type: gradle
+  - path: ./core-rust/Cargo.lock
+    type: cargo
\ No newline at end of file
```

### .snyk
```diff
@@ -1,14 +0,0 @@
-# Snyk (https://snyk.io) policy file, patches or ignores known vulnerabilities.
-version: v1.25.0
-ignore: {}
-patch: {}
-exclude:
-  global:
-    # Snyk reports false positives in those files and sadly
-    # there's no option to ignore specific issues within a file.
-    - core/src/main/java/com/radixdlt/p2p/transport/FrameCodec.java
-    - common/src/main/java/com/radixdlt/crypto/IESEngine.java
-    - common/src/main/java/com/radixdlt/crypto/ECIESCoder.java
-    - cli-tools/src/main/java/com/radixdlt/cloud/AWSSecrets.java
-    - common/src/main/java/com/radixdlt/crypto/ECKeyUtils.java
-    - core/src/test/java/com/radixdlt/api/DummySslContextFactory.java
```

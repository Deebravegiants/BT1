# [?] Revert "[zizmor] Security fixes for workflow vulnerabilities"

## Summary
Severity: Unknown
Chain: VeChain
Component: vechain/thor
Published: 2025-10-21
Source: https://github.com/vechain/thor/commit/32a15d1c218144f15625ab975dfcde664540e148
Type: security-commit

## Details
Revert "[zizmor] Security fixes for workflow vulnerabilities"

## Patch
### .github/workflows/gosec.yaml
```diff
@@ -24,7 +24,7 @@ jobs:
       - name: Run Gosec
         id: gosec-run
         continue-on-error: true
-        uses: securego/gosec@6be2b51fd78feca86af91f5186b7964d76cb1256 # v2.22.10
+        uses: securego/gosec@master
         with:
           args: '-exclude=G104,G115,G304,G406,G507 -exclude-dir=builtin/gen ./...'
 
@@ -39,7 +39,7 @@ jobs:
         uses: actions/checkout@v4
 
       - name: Notify Slack
-        uses: slackapi/slack-github-action@6c661ce58804a1a20f6dc5fbee7f0381b469e001 # v1.25.0
+        uses: slackapi/slack-github-action@v1.25.0
         env:
           SLACK_WEBHOOK_URL: ${{ secrets.GOSEC_SLACK_WEBHOOK }}
         with:
```

### .github/workflows/license-check.yaml
```diff
@@ -13,4 +13,4 @@ jobs:
       - uses: actions/checkout@v4
 
       - name: License Check
-        uses: apache/skywalking-eyes@cd7b195c51fd3d6ad52afceb760719ddc6b3ee91 # v0.6.0
+        uses: apache/skywalking-eyes@v0.6.0
```

### .github/workflows/lint-go.yaml
```diff
@@ -29,7 +29,7 @@ jobs:
           go run golang.org/x/tools/gopls/internal/analysis/modernize/cmd/modernize@latest -test ./...
 
       - name: golangci-lint
-        uses: golangci/golangci-lint-action@4afd733a84b1f43292c63897423277bb7f4313a9 # v8
+        uses: golangci/golangci-lint-action@v8
         with:
           version: v2.2.1
           # use the default if on main branch, otherwise use the pull request config
```

### .github/workflows/on-master-commit.yaml
```diff
@@ -120,7 +120,7 @@ jobs:
           echo "commit_message=$(git show-branch --no-name HEAD)" >> "$GITHUB_ENV"
 
       - name: Notify Slack
-        uses: slackapi/slack-github-action@6c661ce58804a1a20f6dc5fbee7f0381b469e001 # v1.25.0
+        uses: slackapi/slack-github-action@v1.25.0
         env:
           SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
         with:
```

### .github/workflows/on-pre-release.yaml
```diff
@@ -19,7 +19,7 @@ jobs:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         # This step validates that the tag is a pre-release
         run: |
-          prerelease=$(gh release view ${GITHUB_REF_NAME} --json isPrerelease | jq -r '.isPrerelease')
+          prerelease=$(gh release view ${{ github.ref_name }} --json isPrerelease | jq -r '.isPrerelease')
           if [ "$prerelease" != "true" ]; then
             echo "Tag is not a pre-release"
             exit 1
@@ -28,7 +28,7 @@ jobs:
       - name: Validate VERSION
         run: |
           version=$(cat cmd/thor/VERSION)
-          tag="${GITHUB_REF_NAME}"
+          tag="${{ github.ref_name }}"
           tag="${tag#v}"  # Remove the "v" prefix from the tag
           tag="${tag%%-rc.*}" # Remove the "-rc.*" suffix from the tag
           if [ "$tag" != "$version" ]; then
@@ -50,7 +50,7 @@ jobs:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         # This step validates that the tag is an official release
         run: |
-          prerelease=$(gh release view ${GITHUB_REF_NAME} --json isPrerelease | jq -r '.isPrerelease')
+          prerelease=$(gh release view ${{ github.ref_name }} --json isPrerelease | jq -r '.isPrerelease')
           if [ "$prerelease" != "true" ]; then
             echo "Tag is not a release candidate"
             exit 1
```

### .github/workflows/on-release.yaml
```diff
@@ -21,12 +21,12 @@ jobs:
 
       - name: Validate Tag
         run: |
-          node -e "if (!/^v\d+\.\d+\.\d+$/.test('${GITHUB_REF_NAME}')) { console.error('Invalid version provided');process.exit(1);}"
+          node -e "if (!/^v\d+\.\d+\.\d+$/.test('${{ github.ref_name }}')) { console.error('Invalid version provided');process.exit(1);}"
 
       - name: Validate VERSION
         run: |
           version=$(cat cmd/thor/VERSION)
-          tag="${GITHUB_REF_NAME}"
+          tag="${{ github.ref_name }}"
           tag="${tag#v}"  # Remove the "v" prefix from the tag
           if [ "$tag" != "$version" ]; then
             echo "VERSION file does not match tag"
@@ -47,7 +47,7 @@ jobs:
           GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
         # This step validates that the tag is an official release
         run: |
-          prerelease=$(gh release view ${GITHUB_REF_NAME} --json isPrerelease | jq -r '.isPrerelease')
+          prerelease=$(gh release view ${{ github.ref_name }} --json isPrerelease | jq -r '.isPrerelease')
           if [ "$prerelease" != "false" ]; then
             echo "Tag is not an official release"
             exit 1
```

### .github/workflows/publish-docker-images.yaml
```diff
@@ -45,22 +45,22 @@ jobs:
 
       - name: Set up QEMU
         if: ${{ github.event_name != 'pull_request' }}
-        uses: docker/setup-qemu-action@29109295f81e9208d7d86ff1c6c12d2833863392 # v3
+        uses: docker/setup-qemu-action@v3
 
       - name: Set up Docker Buildx
         if: ${{ github.event_name != 'pull_request' }}
-        uses: docker/setup-buildx-action@e468171a9de216ec08956ac3ada2f0791b6bd435 # v3
+        uses: docker/setup-buildx-action@v3
 
       - name: Log in to Docker Hub
-        uses: docker/login-action@5e57cd118135c172c3672efd75eb46360885c0ef # v3
+        uses: docker/login-action@v3
         # Only log in to Docker Hub if the event is a release
         if: ${{ inputs.environment == 'docker-publish' && github.event_name != 'pull_request' }}
         with:
           username: ${{ secrets.DOCKERHUB_USERNAME }}
           password: ${{ secrets.DOCKERHUB_TOKEN }}
 
       - name: Log in to the Container registry
-        uses: docker/login-action@5e57cd118135c172c3672efd75eb46360885c0ef # v3
+        uses: docker/login-action@v3
         if: ${{ github.event_name != 'pull_request' }}
         with:
           registry: ghcr.io
@@ -69,15 +69,15 @@ jobs:
 
       - name: Extract metadata (tags, labels) for Docker
         id: meta
-        uses: docker/metadata-action@c1e51972afc2121e065aed6d45c65596fe445f3f # v5
+        uses: docker/metadata-action@v5
         with:
           # default to ghcr.io for workflow_dispatch
           images: ${{ inputs.images || format('ghcr.io/{0}', github.repository) }}
           # use the branch + sha if workflow_dispatch
           tags: ${{ inputs.tags || format('type=raw,value={0}-{1}', github.ref_name, github.sha) }}
 
       - name: Push to Registry(s)
-        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83 # v6
+        uses: docker/build-push-action@v6
         with:
           context: .
           platforms: ${{ github.event_name != 'pull_request' && 'linux/amd64,linux/arm64' || 'linux/amd64' }}
@@ -89,7 +89,7 @@ jobs:
           labels: ${{ steps.meta.outputs.labels }}
 
       - name: Scan for vulnerabilities
-        uses: crazy-max/ghaction-container-scan@4d8e0acba576e46016cbd65b9ecfc604e85e3990 # v3
+        uses: crazy-max/ghaction-container-scan@v3
         if: ${{ github.event_name == 'pull_request' || github.ref_name == 'master' }}
         with:
           image: ${{ fromJSON(steps.meta.outputs.json).tags[0] }}
```

### .github/workflows/release-binaries.yaml
```diff
@@ -82,7 +82,7 @@ jobs:
           tar czf "${ARCHIVE_NAME##*/}" "$(basename "$RELEASE_BINARY_NAME")"
 
       - name: Upload Binary
-        uses: alexellis/upload-assets@13926a61cdb2cb35f5fdef1c06b8b591523236d3 # 0.4.1
+        uses: alexellis/upload-assets@0.4.1
         env:
           GITHUB_TOKEN: ${{ github.token }}
         with:
@@ -135,7 +135,7 @@ jobs:
           Compress-Archive -Path (Split-Path -Leaf $Env:RELEASE_BINARY_NAME) -DestinationPath (Split-Path -Leaf $Env:ARCHIVE_NAME)
 
       - name: Upload Binary
-        uses: alexellis/upload-assets@13926a61cdb2cb35f5fdef1c06b8b591523236d3 # 0.4.1
+        uses: alexellis/upload-assets@0.4.1
         env:
           GITHUB_TOKEN: ${{ github.token }}
         with:
```

### .github/workflows/test-e2e.yaml
```diff
@@ -25,13 +25,13 @@ jobs:
         uses: actions/checkout@v4
 
       - name: Set up QEMU
-        uses: docker/setup-qemu-action@29109295f81e9208d7d86ff1c6c12d2833863392 # v3
+        uses: docker/setup-qemu-action@v3
 
       - name: Set up Docker Buildx
-        uses: docker/setup-buildx-action@e468171a9de216ec08956ac3ada2f0791b6bd435 # v3
+        uses: docker/setup-buildx-action@v3
 
       - name: Build and export
-        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83 # v6
+        uses: docker/build-push-action@v6
         with:
           context: .
           tags: vechain/thor:${{ github.sha }}
```

### .github/workflows/test-smoke.yaml
```diff
@@ -28,15 +28,15 @@ jobs:
 
       - name: Set up QEMU
         if: steps.download-artifact.outcome == 'failure'
-        uses: docker/setup-qemu-action@29109295f81e9208d7d86ff1c6c12d2833863392 # v3
+        uses: docker/setup-qemu-action@v3
 
       - name: Set up Docker Buildx
         if: steps.download-artifact.outcome == 'failure'
-        uses: docker/setup-buildx-action@e468171a9de216ec08956ac3ada2f0791b6bd435 # v3
+        uses: docker/setup-buildx-action@v3
 
       - name: Build and export
         if: steps.download-artifact.outcome == 'failure'
-        uses: docker/build-push-action@263435318d21b8e681c14492fe198d362a7d2c83 # v6
+        uses: docker/build-push-action@v6
         with:
           context: .
           tags: vechain/thor:${{ github.sha }}
@@ -70,13 +70,13 @@ jobs:
       
           if [ "${{ github.event_name }}" = "pull_request" ]; then
             # For pull_request events, we only look at the PR's base branch
-            if [[ "${GITHUB_EVENT_PULL_REQUEST_BASE_REF}" == release/* ]]; then
-              REF="${GITHUB_EVENT_PULL_REQUEST_BASE_REF}"
+            if [[ "${{ github.event.pull_request.base.ref }}" == release/* ]]; then
+              REF="${{ github.event.pull_request.base.ref }}"
             fi
           else
             # For push events, we check the branch or tag that was pushed
-            if [[ "${GITHUB_REF_NAME}" == release/* ]]; then
-              REF="${GITHUB_REF_NAME}"
+            if [[ "${{ github.ref_name }}" == release/* ]]; then
+              REF="${{ github.ref_name }}"
             fi
           fi
 
@@ -89,8 +89,6 @@ jobs:
           fi
 
           echo "DRAUPNIR REF: $(<$GITHUB_OUTPUT)"
-        env:
-          GITHUB_EVENT_PULL_REQUEST_BASE_REF: ${{ github.event.pull_request.base.ref }}
 
       - name: Checkout
         uses: actions/checkout@v4
```

### .github/workflows/test.yaml
```diff
@@ -58,7 +58,7 @@ jobs:
         run: make test-coverage
 
       - name: Upload coverage to Codecov
-        uses: codecov/codecov-action@5a1091511ad55cbe89839c7260b706298ca349f7 # v5
+        uses: codecov/codecov-action@v5
         if: ${{ github.repository == 'vechain/thor' }}
         with:
           fail_ci_if_error: true
```

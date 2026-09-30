# [?] Fix race condition on osmosis dev images push (#8511)

## Summary
Severity: Unknown
Chain: Osmosis
Component: osmosis-labs/osmosis
Published: 2024-07-15
Source: https://github.com/osmosis-labs/osmosis/commit/58e7042c0eac308d2b8c89993eb6aeef5b83f8dd
Type: security-commit

## Details
Fix race condition on osmosis dev images push (#8511)

## Patch
### .github/workflows/push-dev-docker-images.yml
```diff
@@ -39,6 +39,9 @@ jobs:
         uses: actions/checkout@v4
         with:
           fetch-depth: 0
+      -
+        name: Set up QEMU
+        uses: docker/setup-qemu-action@v3
       -
         name: Set up Docker Buildx
         uses: docker/setup-buildx-action@v3
@@ -74,7 +77,7 @@ jobs:
           file: Dockerfile
           context: .
           push: true
-          platforms: linux/amd64
+          platforms: linux/amd64,linux/arm64
           build-args: |
             GO_VERSION=${{ env.GO_VERSION }}
             RUNNER_IMAGE=${{ env.RUNNER_BASE_IMAGE_ALPINE }}
@@ -89,20 +92,19 @@ jobs:
           file: tests/e2e/initialization/init.Dockerfile
           context: .
           push: true
-          platforms: linux/amd64
+          platforms: linux/amd64,linux/arm64
           build-args: |
             E2E_SCRIPT_NAME=chain
           tags: |
             ${{ env.OSMOSIS_INIT_CHAIN_IMAGE_REPOSITORY }}:${{ env.DOCKER_IMAGE_TAG }}
-
       -
         name: Build and Push Cosmovisor Docker Images
         uses: docker/build-push-action@v6
         with:
           file: Dockerfile.cosmovisor
           context: .
           push: true
-          platforms: linux/amd64
+          platforms: linux/amd64,linux/arm64
           build-args: |
             GO_VERSION=${{ env.GO_VERSION }}
             RUNNER_IMAGE=${{ env.RUNNER_BASE_IMAGE_ALPINE }}
@@ -111,67 +113,3 @@ jobs:
             COSMOVISOR_VERSION=${{ env.COSMOVISOR_VERSION }}
           tags: |
             ${{ env.OSMOSIS_DEV_IMAGE_COSMOVISOR_REPOSITORY }}:${{ env.DOCKER_IMAGE_TAG }}
-
-  push-docker-images-arm:
-    runs-on: buildjet-2vcpu-ubuntu-2204-arm
-    steps:
-      -
-        name: Check out repo
-        uses: actions/checkout@v4
-        with:
-          fetch-depth: 0
-      -
-        name: Set up Docker Buildx
-        uses: docker/setup-buildx-action@v3
-      -
-        name: Login to DockerHub
-        uses: docker/login-action@v3
-        with:
-          username: ${{ secrets.DOCKERHUB_USERNAME }}
-          password: ${{ secrets.DOCKERHUB_TOKEN }}
-      -
-        name: Find go version
-        run: |
-          GO_VERSION=$(cat go.mod | grep -E 'go [0-9].[0-9]+' | cut -d ' ' -f 2)
-          echo "GO_VERSION=$GO_VERSION" >> $GITHUB_ENV
-      -
-        name: Create Docker Image Tag for release candidate
-        if: startsWith(github.ref, 'refs/tags/v')
-        run: |
-          GITHUB_TAG=${{ github.ref_name }}
-          echo "DOCKER_IMAGE_TAG=${GITHUB_TAG#v}" >> $GITHUB_ENV
-          echo "OSMOSIS_VERSION=${{ github.ref_name }}" >> $GITHUB_ENV
-      -
-        name: Create Docker Image Tag for vN.x branch
-        if: ${{ !startsWith(github.ref, 'refs/tags/v') }}
-        run: |
-          SHORT_SHA=$(echo ${GITHUB_SHA} | cut -c1-8)
-          echo "DOCKER_IMAGE_TAG=${{ github.ref_name }}-${SHORT_SHA}-$(date +%s)" >> $GITHUB_ENV
-          echo "OSMOSIS_VERSION=${{ github.ref_name }}-$SHORT_SHA" >> $GITHUB_ENV
-      -
-        name: Build and Push Docker Images
-        uses: docker/build-push-action@v6
-        with:
-          file: Dockerfile
-          context: .
-          push: true
-          platforms: linux/arm64
-          build-args: |
-            GO_VERSION=${{ env.GO_VERSION }}
-            RUNNER_IMAGE=${{ env.RUNNER_BASE_IMAGE_ALPINE }}
-            GIT_VERSION=${{ env.OSMOSIS_VERSION }}
-            GIT_COMMIT=${{ github.sha }}
-          tags: |
-            ${{ env.OSMOSIS_DEV_IMAGE_REPOSITORY }}:${{ env.DOCKER_IMAGE_TAG }}
-      -
-        name: Build and Push E2E Init Docker Images
-        uses: docker/build-push-action@v6
-        with:
-          file: tests/e2e/initialization/init.Dockerfile
-          context: .
-          push: true
-          platforms: linux/arm64
-          build-args: |
-            E2E_SCRIPT_NAME=chain
-          tags: |
-            ${{ env.OSMOSIS_INIT_CHAIN_IMAGE_REPOSITORY }}:${{ env.DOCKER_IMAGE_TAG }}
```

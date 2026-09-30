# [?] feat(ci): add Docker Scout vulnerabilities scanning (#8871)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2024-09-24
Source: https://github.com/ZcashFoundation/zebra/commit/ac1242a189e6f22bb132a01bc1ab3b89daedc041
Type: security-commit

## Details
feat(ci): add Docker Scout vulnerabilities scanning (#8871)

* feat(ci): add Docker Scout vulnerabilities scanning

* fix(scout): add missing `environment` command

Co-authored-by: Marek <mail@marek.onl>

---------

Co-authored-by: Marek <mail@marek.onl>

## Patch
### .github/workflows/sub-build-docker-image.yml
```diff
@@ -4,6 +4,7 @@
 # - Uses Docker Buildx for improved build performance and caching.
 # - Builds the Docker image and pushes it to both Google Artifact Registry and potentially DockerHub, depending on release type.
 # - Manages caching strategies to optimize build times across different branches.
+# - Uses Docker Scout to display vulnerabilities and recommendations for the latest built image.
 name: Build docker image
 
 on:
@@ -75,6 +76,7 @@ jobs:
     permissions:
       contents: 'read'
       id-token: 'write'
+      pull-requests: write # for `docker-scout` to be able to write the comment
     env:
       DOCKER_BUILD_SUMMARY: ${{ vars.DOCKER_BUILD_SUMMARY }}
     steps:
@@ -150,7 +152,7 @@ jobs:
       # Setup Docker Buildx to use Docker Build Cloud
       - name: Set up Docker Buildx
         id: buildx
-        uses: docker/setup-buildx-action@v3
+        uses: docker/setup-buildx-action@v3.6.1
         with:
           version: "lab:latest"
           driver: cloud
@@ -179,3 +181,32 @@ jobs:
           # Don't read from the cache if the caller disabled it.
           # https://docs.docker.com/engine/reference/commandline/buildx_build/#options
           no-cache: ${{ inputs.no_cache }}
+
+        # For the latest built image, display:
+        # - the vulnerabilities (ignoring the base image, and only displaying vulnerabilities with a critical or high security severity)
+        # - the available recommendations
+        # - compare it to the latest image indexed in Docker Hub (only displaying changed packages and vulnerabilities that already have a fix)
+        #
+        # Record the image to Scout environment based on the event type, for example:
+        # - `prod` for a release event
+        # - `stage` for a push event to the main branch
+        # - `dev` for a pull request event
+      - name: Docker Scout
+        id: docker-scout
+        uses: docker/scout-action@v1.13.0
+        # We only run Docker Scout on the `runtime` target, as the other targets are not meant to be released
+        # and are commonly used for testing, and thus are ephemeral.
+        # TODO: Remove the `contains` check once we have a better way to determine if just new vulnerabilities are present.
+        # See: https://github.com/docker/scout-action/issues/56
+        if: ${{ inputs.dockerfile_target == 'runtime' && contains(github.event.pull_request.title, 'Release v') }}
+        with:
+          command: cves,recommendations,compare,environment
+          image: us-docker.pkg.dev/${{ vars.GCP_PROJECT }}/zebra/${{ inputs.image_name }}:${{ steps.meta.outputs.version }}
+          to: zfnd/zebra:latest
+          ignore-base: true
+          ignore-unchanged: true
+          only-fixed: true
+          only-severities: critical,high
+          environment: ${{ (github.event_name == 'release' && !github.event.release.prerelease && 'prod') || (github.event_name == 'push' && github.ref_name == 'main' && 'stage') || (github.event_name == 'pull_request' && 'dev') }}
+          organization: zfnd
+          github-token: ${{ secrets.GITHUB_TOKEN }} # to be able to write the comment
```

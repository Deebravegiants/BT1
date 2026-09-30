# [?] fix: Update curl to 7.88.1-10+deb12u4 for CVE-2023-38545

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2023-10-11
Source: https://github.com/radixdlt/babylon-node/commit/2cd595b3270122c212d570231affb0352da34cb4
Type: security-commit

## Details
fix: Update curl to 7.88.1-10+deb12u4 for CVE-2023-38545

## Patch
### Dockerfile
```diff
@@ -88,7 +88,8 @@ RUN apt-get update \
   && apt-get -y --no-install-recommends install \
     ca-certificates \
     build-essential=12.9 \
-    curl=7.88.1-10+deb12u3 \
+    # https://security-tracker.debian.org/tracker/CVE-2023-38545
+    curl=7.88.1-10+deb12u4 \
     g++-aarch64-linux-gnu \
     g++-x86-64-linux-gnu \
     libc6-dev-arm64-cross=2.36-8cross1 \
@@ -203,9 +204,11 @@ LABEL org.opencontainers.image.authors="devops@radixdlt.com"
 RUN apt-get update -y \
   && apt-get -y --no-install-recommends install \
     openjdk-17-jre-headless=17.0.8+7-1~deb12u1 \
-    curl=7.88.1-10+deb12u3 \
+    # https://security-tracker.debian.org/tracker/CVE-2023-38545
+    curl=7.88.1-10+deb12u4 \
     gettext-base=0.21-12 \
     daemontools=1:0.76-8.1 \
+    # https://security-tracker.debian.org/tracker/CVE-2023-4911
     # Fixes CVE-2023-4911 can be removed when we update the base OS image to include this fix
     # docker run -it debian:12.1-slim ldd --version
     # This fix can be removed as long as the version printed in the above command is 2.36-9+deb12u3 or above
```

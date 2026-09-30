# [?] CVE-2023-4911 for main branch (#714)

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2023-10-10
Source: https://github.com/radixdlt/babylon-node/commit/2ddf340c5244f68a9482a156d7c9f930af6691d6
Type: security-commit

## Details
CVE-2023-4911 for main branch (#714)

https://security-tracker.debian.org/tracker/CVE-2023-4911

## Patch
### Dockerfile
```diff
@@ -24,7 +24,7 @@ ARG WGET_VERSION="1.21.3-1+b2"
 RUN apt-get update \
   && apt-get install -y --no-install-recommends \
     docker.io=20.10.24+dfsg1-1+b3 \
-    libssl-dev=3.0.9-1 \
+    libssl-dev=3.0.11-1~deb12u1 \
     pkg-config=1.8.1-1 \
     unzip=6.0-28 \
     wget=${WGET_VERSION} \
@@ -88,12 +88,12 @@ RUN apt-get update \
   && apt-get -y --no-install-recommends install \
     ca-certificates \
     build-essential=12.9 \
-    curl=7.88.1-10+deb12u1 \
+    curl=7.88.1-10+deb12u3 \
     g++-aarch64-linux-gnu \
     g++-x86-64-linux-gnu \
     libc6-dev-arm64-cross=2.36-8cross1 \
-    libclang-dev=1:14.0-55.6 \
-    libssl-dev=3.0.9-1 \
+    libclang-dev=1:14.0-55.7~deb12u1 \
+    libssl-dev=3.0.11-1~deb12u1 \
     pkg-config=1.8.1-1 \
   && rm -rf /var/lib/apt/lists/*
 
@@ -203,9 +203,13 @@ LABEL org.opencontainers.image.authors="devops@radixdlt.com"
 RUN apt-get update -y \
   && apt-get -y --no-install-recommends install \
     openjdk-17-jre-headless=17.0.8+7-1~deb12u1 \
-    curl=7.88.1-10+deb12u1 \
+    curl=7.88.1-10+deb12u3 \
     gettext-base=0.21-12 \
     daemontools=1:0.76-8.1 \
+    # Fixes CVE-2023-4911 can be removed when we update the base OS image to include this fix
+    # docker run -it debian:12.1-slim ldd --version
+    # This fix can be removed as long as the version printed in the above command is 2.36-9+deb12u3 or above
+    libc6=2.36-9+deb12u3 \ 
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*
 
```

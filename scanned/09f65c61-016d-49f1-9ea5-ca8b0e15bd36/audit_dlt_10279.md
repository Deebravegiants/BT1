# [?] add command to check if security fix can be removed

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2023-10-09
Source: https://github.com/radixdlt/babylon-node/commit/b73f5479c9eb237be4b80c7eff06ffb80f1fc4e5
Type: security-commit

## Details
add command to check if security fix can be removed

## Patch
### Dockerfile
```diff
@@ -207,6 +207,8 @@ RUN apt-get update -y \
     gettext-base=0.21-12 \
     daemontools=1:0.76-8.1 \
     # Fixes CVE-2023-4911 can be removed when we update the base OS image to include this fix
+    # docker run -it debian:12.1-slim ldd --version
+    # This fix can bre removed as long as the version printed in the above command is 2.36-9+deb12u3 or above
     libc6=2.36-9+deb12u3 \ 
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*
```

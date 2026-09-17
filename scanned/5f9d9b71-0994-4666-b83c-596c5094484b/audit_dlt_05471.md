# [?] Fix / Update openjdk version due to security fix (#853)

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/babylon-node
Published: 2024-02-27
Source: https://github.com/radixdlt/babylon-node/commit/dc661bf12f1b72b3a6654fa6f3c6b986acdec174
Type: security-commit

## Details
Fix / Update openjdk version due to security fix (#853)

> [!IMPORTANT]
>
> * Please read our [Contributing Guidelines](CONTRIBUTING.md) before
opening a PR.
> * Before creating your PR, please ensure you have used the _correct
base branch_ as per the [branching
strategy](/docs/branching-strategy.md), both for branching from, and in
the PR UI above.
>   * For most code changes, this is `develop`.
>   * For stand-alone docs changes, this is `main`.
> * For workflow changes, this is the oldest supported `release/*`
branch.
> * Please remove these sections as you fill out your PR.
> 

## Summary

> [!TIP]
> 
> Start with the context of your PR. Why are you making this change?
What does it address? Link back to an issue if relevant.
> 
> Then summarise the changes that were made. Bullet points are fine.

## Details

> [!TIP]
> 
> This section is optional. Go into more detail about the changes that
were made, or the thinking behind the changes.

## Testing

> [!TIP]
> 
> Explain what testing / verification is done, including manual testing
or automated testing.

### Dockerfile
```diff
@@ -31,7 +31,7 @@ RUN apt-get update \
     wget=${WGET_VERSION} \
     software-properties-common=0.99.30-4 \
   && apt-get install -y --no-install-recommends \
-    openjdk-17-jdk=17.0.9+9-1~deb12u1 \
+    openjdk-17-jdk=17.0.10+7-1~deb12u1 \
   && apt-get clean \
   && rm -rf /var/lib/apt/lists/*
 
@@ -206,7 +206,7 @@ LABEL org.opencontainers.image.authors="devops@radixdlt.com"
 # - curl is needed for the docker-healthcheck
 RUN apt-get update -y \
   && apt-get -y --no-install-recommends install \
-    openjdk-17-jre-headless=17.0.9+9-1~deb12u1 \
+    openjdk-17-jre-headless=17.0.10+7-1~deb12u1 \
     # https://security-tracker.debian.org/tracker/CVE-2023-38545
     curl=7.88.1-10+deb12u5 \
     gettext-base=0.21-12 \
```

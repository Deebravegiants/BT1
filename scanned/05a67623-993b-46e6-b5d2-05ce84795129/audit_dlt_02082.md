# [?] fix: docker repository initialization race condition

## Summary
Severity: Unknown
Chain: IPFS
Component: ipfs/kubo
Published: 2023-06-26
Source: https://github.com/ipfs/kubo/commit/d1e31417521913dcdc6c90a6da13313e37ea807d
Type: security-commit

## Details
fix: docker repository initialization race condition

When running the health check command without passing the `--api` command line flag and if the Kubo daemon is not active, executing `ipfs dag stat` will initialize the repository. It is common for the health check command to be run with root privileges. As a result, the repository will be owned by the root user. Then, if the Kubo daemon process attempts to access the repository later on, it will encounter a permission denied error because it runs as a non-privileged user by default.

Hence, this modification simply provides the `--api` flag to the `ipfs dag stat` command. Given that we are operating within the limited confines of a docker container, we can make a few assumptions. I can't come up with a scenario where one would desire to assign a different port to the internal API rather than using the default 5001. Therefore, I have hard-coded the value accordingly.

(cherry picked from commit 1972a49f91e878007c7efa1f6eb55ea19d97184b)

## Patch
### Dockerfile
```diff
@@ -118,7 +118,7 @@ ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/start_ipfs"]
 # Healthcheck for the container
 # QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn is the CID of empty folder
 HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
-  CMD ipfs dag stat /ipfs/QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn || exit 1
+  CMD ipfs --api=/ip4/127.0.0.1/tcp/5001 dag stat /ipfs/QmUNLLsPACCz1vLxQVkXqqLX5R1X345qqfHbsf67hvA3Nn || exit 1
 
 # Execute the daemon subcommand by default
 CMD ["daemon", "--migrate=true", "--agent-version-suffix=docker"]
```

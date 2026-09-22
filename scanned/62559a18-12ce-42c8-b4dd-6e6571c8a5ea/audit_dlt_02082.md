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

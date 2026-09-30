# [C] Dockge Path Traversal via Unvalidated Stack Name Allows Arbitrary Compose and .env Disclosure and Arbitrary Directory Deletion

## Summary
Severity: Critical
Advisory: CVE-2026-73040
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-73040
Type: osv

## Details
Dockge validates a stack name only on the write path. In backend/stack.ts the allow-list check in validate(), which requires the name to match ^[a-z0-9_-]+$, is reached from save() alone, while the path getter returns path.join(this.server.stacksDir, this.name) and Stack.getStack builds path.join(server.stacksDir, stackName) with no check. The socket handlers in backend/agent-socket-handlers/docker-socket-handler.ts confirm the caller is logged in and that the name is a string, then pass it straight to Stack.getStack, so a name containing traversal sequences resolves outside the managed stacks directory. An authenticated user can therefore read the composeENV and composeYAML values of any directory the server process can reach, which discloses the secrets in that directory's .env or Compose file, and can invoke delete(), which runs docker compose down and then fsAsync.rm on the traversed path with recursive and force set, removing that directory. Disclosure is limited to files named .env or an accepted Compose filename, and deletion requires the target directory to hold a valid Compose file so that docker compose down exits successfully. Dockge commonly runs as root with access to the Docker socket, so the reachable set includes unrelated applications on the host. Instances configured with disableAuth, a supported option that logs the caller in as admin automatically, expose both operations without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73040.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73040
- https://www.vulncheck.com/advisories/dockge-path-traversal-via-unvalidated-stack-name-allows-arbitrary-compose-and-env-disclosure-and-arbitrary-directory-deletion
- https://github.com/louislam/dockge/issues/994
- https://github.com/louislam/dockge
- https://github.com/louislam/dockge/blob/1.5.0/backend/agent-socket-handlers/docker-socket-handler.ts#L43-L78
- https://github.com/louislam/dockge/blob/1.5.0/backend/stack.ts#L155-L157
- https://github.com/louislam/dockge/blob/1.5.0/backend/stack.ts#L218-L232
- https://github.com/louislam/dockge/blob/1.5.0/backend/stack.ts#L377-L379

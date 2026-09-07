# [H] Node DOS by way of memory exhaustion through ExecSync request in CRI-O

## Summary
Severity: High
Advisory: GHSA-fcm2-6c3h-pg6j
CVE: CVE-2022-1708
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-06
Source: https://github.com/advisories/GHSA-fcm2-6c3h-pg6j
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=1.24.0 <1.24.1
- Go: `github.com/cri-o/cri-o` — affected >=1.23.0 <1.23.3
- Go: `github.com/cri-o/cri-o` — affected >=0 <1.22.5

## Details
### Description
An ExecSync request runs a command in a container and returns the output to the Kubelet. It is used for readiness and liveness probes within a pod. The way CRI-O runs ExecSync commands is through conmon. CRI-O asks conmon to start the process, and conmon writes the output to disk. CRI-O then reads the output and returns it to the Kubelet.

If the output of the command is large enough, it is possible to exhaust the memory (or disk usage) of the node. The following deployment is an example yaml file that will output around 8GB of ‘A’ characters, which would be written to disk by conmon and read by CRI-O.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment100
spec:
  selector:
    matchLabels:
      app: nginx
  replicas: 2
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        lifecycle:
          postStart:
            exec:
              command: ["/bin/sh", "-c", "seq 1 50000000`; do echo -n 'aaaaaaaaaaaaaaaa'; done"]
```

### Impact
It is possible for the node to be exhausted of memory or disk space, depending on the node the command is being run on. What is further problematic is that the memory and disk usage aren't attributed to the container, as this file and its processing are implementation details of CRI-O. The consequence of the exhaustion is that other services on the node, e.g. other containers, will be unable to allocate memory and thus causing a denial of service.

### Patches
This vulnerability will be fixed in 1.24.1, 1.23.3, 1.22.5, v1.21.8, v1.20.8, v1.19.7

### Workarounds
At the time of writing, no workaround exists other than ensuring only trusted images are used.

### References
https://github.com/containerd/containerd/security/advisories/GHSA-5ffw-gxpp-mxpf

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the CRI-O repo](http://github.com/cri-o/cri-o/issues)
* To make a report, email your vulnerability to the private
[cncf-crio-security@lists.cncf.io](mailto:cncf-crio-security@lists.cncf.io) list
with the security details and the details expected for [all CRI-O bug
reports](https://github.com/cri-o/cri-o/blob/main/.github/ISSUE_TEMPLATE/bug-report.yml).

### Credits
Disclosed by Ada Logics in a security audit sponsored by CNCF and facilitated by OSTIF.

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-fcm2-6c3h-pg6j
- https://nvd.nist.gov/vuln/detail/CVE-2022-1708
- https://github.com/cri-o/cri-o/commit/f032cf649ecc7e0c46718bd9e7814bfb317cb544
- https://bugzilla.redhat.com/show_bug.cgi?id=2085361
- https://github.com/cri-o/cri-o

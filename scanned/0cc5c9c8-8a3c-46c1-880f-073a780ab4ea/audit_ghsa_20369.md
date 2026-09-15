# [M] containerd CRI plugin: Host memory exhaustion through ExecSync

## Summary
Severity: Medium
Advisory: GHSA-5ffw-gxpp-mxpf
CVE: CVE-2022-31030
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-06
Source: https://github.com/advisories/GHSA-5ffw-gxpp-mxpf
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.5.13
- Go: `github.com/containerd/containerd` — affected >=1.6.0 <1.6.6

## Details
### Impact

A bug was found in containerd's CRI implementation where programs inside a container can cause the containerd daemon to consume memory without bound during invocation of the `ExecSync` API.  This can cause containerd to consume all available memory on the computer, denying service to other legitimate workloads.  Kubernetes and crictl can both be configured to use containerd's CRI implementation; `ExecSync` may be used when running probes or when executing processes via an "exec" facility.

### Patches

This bug has been fixed in containerd 1.6.6 and 1.5.13.  Users should update to these versions to resolve the issue.

### Workarounds

Ensure that only trusted images and commands are used. 

### References

* Similar fix in cri-o's CRI implementation https://github.com/cri-o/cri-o/security/advisories/GHSA-fcm2-6c3h-pg6j

### Credits

The containerd project would like to thank David Korczynski and Adam Korczynski of ADA Logics for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/main/SECURITY.md) during a security audit sponsored by CNCF and facilitated by OSTIF.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-5ffw-gxpp-mxpf
- https://nvd.nist.gov/vuln/detail/CVE-2022-31030
- https://github.com/containerd/containerd/commit/c1bcabb4541930f643aa36a2b38655e131346382
- https://github.com/containerd/containerd
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/REOZCUAPCA7NFDWYBDYX6EYXWLHABKBO
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WSIGDBHAB3I75JBJNGWEPBTJPS2FOVHD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/REOZCUAPCA7NFDWYBDYX6EYXWLHABKBO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WSIGDBHAB3I75JBJNGWEPBTJPS2FOVHD
- https://security.gentoo.org/glsa/202401-31
- https://www.debian.org/security/2022/dsa-5162
- http://www.openwall.com/lists/oss-security/2022/06/07/1

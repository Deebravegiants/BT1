# [M] containerd-shim API Exposed to Host Network Containers

## Summary
Severity: Medium
Advisory: GHSA-36xw-fx78-c5r4
CVE: CVE-2020-15257
CWE: CWE-669
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-24
Source: https://github.com/advisories/GHSA-36xw-fx78-c5r4
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.3.9
- Go: `github.com/containerd/containerd` — affected >=1.4.0 <1.4.3

## Details
## Impact

Access controls for the shim’s API socket verified that the connecting process had an effective UID of 0, but did not otherwise restrict access to the abstract Unix domain socket. This would allow malicious containers running in the same network namespace as the shim, with an effective UID of 0 but otherwise reduced privileges, to cause new processes to be run with elevated privileges.

### Specific Go Packages Affected
github.com/containerd/containerd/cmd

## Patches

This vulnerability has been fixed in containerd 1.3.9 and 1.4.3.  Users should update to these versions as soon as they are released.  It should be noted that containers started with an old version of containerd-shim should be stopped and restarted, as running containers will continue to be vulnerable even after an upgrade.

## Workarounds

If you are not providing the ability for untrusted users to start containers in the same network namespace as the shim (typically the "host" network namespace, for example with `docker run --net=host` or `hostNetwork: true` in a Kubernetes pod) and run with an effective UID of 0, you are not vulnerable to this issue.

If you are running containers with a vulnerable configuration, you can deny access to all abstract sockets with AppArmor by adding a line similar to `deny unix addr=@**,` to your policy.

It is best practice to run containers with a reduced set of privileges, with a non-zero UID, and with isolated namespaces.  The containerd maintainers strongly advise against sharing namespaces with the host. Reducing the set of isolation mechanisms used for a container necessarily increases that container's privilege, regardless of what container runtime is used for running that container.

## Credits

The containerd maintainers would like to thank Jeff Dileo of NCC Group for responsibly disclosing this issue in accordance with the [containerd security policy](https://github.com/containerd/project/blob/master/SECURITY.md) and for reviewing the patch.

## For more information

If you have any questions or comments about this advisory:


* [Open an issue](https://github.com/containerd/containerd/issues/new/choose)
* Email us at security@containerd.io if you think you’ve found a security bug.

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-36xw-fx78-c5r4
- https://nvd.nist.gov/vuln/detail/CVE-2020-15257
- https://github.com/containerd/containerd/commit/4a4bb851f5da563ff6e68a83dc837c7699c469ad
- https://github.com/containerd/containerd/releases/tag/v1.4.3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LNKXLOLZWO5FMAPX63ZL7JNKTNNT5NQD
- https://research.nccgroup.com/2020/12/10/abstract-shimmer-cve-2020-15257-host-networking-is-root-equivalent-again
- https://security.gentoo.org/glsa/202105-33
- https://www.debian.org/security/2021/dsa-4865

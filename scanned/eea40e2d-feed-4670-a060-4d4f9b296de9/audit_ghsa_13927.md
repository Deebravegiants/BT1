# [M] Supplementary groups are not set up properly in github.com/containerd/containerd

## Summary
Severity: Medium
Advisory: GHSA-hmfx-3pcx-653p
CVE: CVE-2023-25173
CWE: CWE-269, CWE-863
Ecosystem: Go
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-02-16
Source: https://github.com/advisories/GHSA-hmfx-3pcx-653p
Type: github-advisory

## Affected
- Go: `github.com/containerd/containerd` — affected >=0 <1.5.18
- Go: `github.com/containerd/containerd` — affected >=1.6.0 <1.6.18

## Details
### Impact

A bug was found in containerd where supplementary groups are not set up properly inside a container.  If an attacker has direct access to a container and manipulates their supplementary group access, they may be able to use supplementary group access to bypass primary group restrictions in some cases, potentially gaining access to sensitive information or gaining the ability to execute code in that container.

Downstream applications that use the containerd client library may be affected as well.

### Patches
This bug has been fixed in containerd v1.6.18 and v.1.5.18.  Users should update to these versions and recreate containers to resolve this issue.  Users who rely on a downstream application that uses containerd's client library should check that application for a separate advisory and instructions.

### Workarounds

Ensure that the `"USER $USERNAME"` Dockerfile instruction is not used.  Instead, set the container entrypoint to a value similar to `ENTRYPOINT ["su", "-", "user"]` to allow `su` to properly set up supplementary groups.

### References

- https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation/
- Docker/Moby: CVE-2022-36109, fixed in Docker 20.10.18
- CRI-O: CVE-2022-2995, fixed in CRI-O 1.25.0
- Podman: CVE-2022-2989, fixed in Podman 3.0.1 and 4.2.0
- Buildah: CVE-2022-2990, fixed in Buildah 1.27.1

Note that CVE IDs apply to a particular implementation, even if an issue is common.

### For more information

If you have any questions or comments about this advisory:

* Open an issue in [containerd](https://github.com/containerd/containerd/issues/new/choose)
* Email us at [security@containerd.io](mailto:security@containerd.io)

To report a security issue in containerd:
* [Report a new vulnerability](https://github.com/containerd/containerd/security/advisories/new)
* Email us at [security@containerd.io](mailto:security@containerd.io)

## References
- https://github.com/containerd/containerd/security/advisories/GHSA-hmfx-3pcx-653p
- https://github.com/moby/moby/security/advisories/GHSA-rc4r-wh2q-q6c4
- https://nvd.nist.gov/vuln/detail/CVE-2023-25173
- https://github.com/containerd/containerd/commit/133f6bb6cd827ce35a5fb279c1ead12b9d21460a
- https://github.com/advisories/GHSA-4wjj-jwc9-2x96
- https://github.com/advisories/GHSA-fjm8-m7m6-2fjp
- https://github.com/advisories/GHSA-phjr-8j92-w5v7
- https://github.com/containerd/containerd
- https://github.com/containerd/containerd/releases/tag/v1.5.18
- https://github.com/containerd/containerd/releases/tag/v1.6.18
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYZOKMMVX4SIEHPJW3SJUQGMO5YZCPHC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XNF4OLYZRQE75EB5TW5N42FSXHBXGWFE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZTE4ITXXPIWZEQ4HYQCB6N6GZIMWXDAI
- https://pkg.go.dev/vuln/GO-2023-1574
- https://www.benthamsgaze.org/2022/08/22/vulnerability-in-linux-containers-investigation-and-mitigation

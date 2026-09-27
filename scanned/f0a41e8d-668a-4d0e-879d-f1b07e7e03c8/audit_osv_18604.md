# [H] CVE-2020-28914

## Summary
Severity: High
Advisory: CVE-2020-28914
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-11-17
Source: https://osv.dev/vulnerability/CVE-2020-28914
Type: osv

## Details
An improper file permissions vulnerability affects Kata Containers prior to 1.11.5. When using a Kubernetes hostPath volume and mounting either a file or directory into a container as readonly, the file/directory is mounted as readOnly inside the container, but is still writable inside the guest. For a container breakout situation, a malicious guest can potentially modify or delete files/directories expected to be read-only.

## References
- https://github.com/kata-containers/kata-containers/pull/1062
- https://github.com/kata-containers/runtime/pull/3042
- https://github.com/kata-containers/runtime/pull/3051
- https://github.com/kata-containers/runtime/releases/tag/1.11.5
- https://github.com/kata-containers/runtime/releases/tag/1.12.0

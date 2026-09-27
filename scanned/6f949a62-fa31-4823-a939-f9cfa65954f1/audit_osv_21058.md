# [M] CVE-2021-4024

## Summary
Severity: Medium
Advisory: CVE-2021-4024
Aliases: GHSA-3cf2-x423-x582, GO-2022-0281
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-4024
Type: osv

## Details
A flaw was found in podman. The `podman machine` function (used to create and manage Podman virtual machine containing a Podman process) spawns a `gvproxy` process on the host system. The `gvproxy` API is accessible on port 7777 on all IP addresses on the host. If that port is open on the host's firewall, an attacker can potentially use the `gvproxy` API to forward ports on the host to ports in the VM, making private services on the VM accessible to the network. This issue could be also used to interrupt the host's services by forwarding all ports to the VM.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QFFVJ6S3ZRMPDYB7KYAWEMDHXFZYQPU3/
- https://github.com/containers/podman/releases/tag/v3.4.3
- https://bugzilla.redhat.com/show_bug.cgi?id=2026675%2C

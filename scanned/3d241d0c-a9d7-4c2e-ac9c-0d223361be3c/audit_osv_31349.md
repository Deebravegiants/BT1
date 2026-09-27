# [M] Podman: buildah: cri-o: symlink traversal vulnerability in the containers/storage library can cause denial of service (dos)

## Summary
Severity: Medium
Advisory: CVE-2024-9676
Aliases: GHSA-wq2p-5pc6-wpgf
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-15
Source: https://osv.dev/vulnerability/CVE-2024-9676
Type: osv

## Details
A vulnerability was found in Podman, Buildah, and CRI-O. A symlink traversal vulnerability in the containers/storage library can cause Podman, Buildah, and CRI-O to hang and result in a denial of service via OOM kill when running a malicious image using an automatically assigned user namespace (`--userns=auto` in Podman and Buildah). The containers/storage library will read /etc/passwd inside the container, but does not properly validate if that file is a symlink, which can be used to cause the library to read an arbitrary file on the host.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/containers/storage/
- https://access.redhat.com/errata/RHSA-2024:10289
- https://access.redhat.com/errata/RHSA-2024:8418
- https://access.redhat.com/errata/RHSA-2024:8428
- https://access.redhat.com/errata/RHSA-2024:8437
- https://access.redhat.com/errata/RHSA-2024:8686
- https://access.redhat.com/errata/RHSA-2024:8690
- https://access.redhat.com/errata/RHSA-2024:8694
- https://access.redhat.com/errata/RHSA-2024:8700
- https://access.redhat.com/errata/RHSA-2024:8984
- https://access.redhat.com/errata/RHSA-2024:9051
- https://access.redhat.com/errata/RHSA-2024:9454
- https://access.redhat.com/errata/RHSA-2024:9459
- https://access.redhat.com/errata/RHSA-2024:9926
- https://access.redhat.com/errata/RHSA-2025:0876
- https://access.redhat.com/errata/RHSA-2025:2454
- https://access.redhat.com/errata/RHSA-2025:2710
- https://access.redhat.com/errata/RHSA-2025:3301

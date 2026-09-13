# [M] CVE-2021-32847

## Summary
Severity: Medium
Advisory: CVE-2021-32847
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-02-20
Source: https://osv.dev/vulnerability/CVE-2021-32847
Type: osv

## Details
HyperKit is a toolkit for embedding hypervisor capabilities in an application. In versions 0.20210107 and prior, a malicious guest can trigger a vulnerability in the host by abusing the disk driver that may lead to the disclosure of the host memory into the virtualized guest. This issue is fixed in commit cf60095a4d8c3cb2e182a14415467afd356e982f.

## References
- https://github.com/moby/hyperkit/commit/cf60095a4d8c3cb2e182a14415467afd356e982f
- https://github.com/moby/hyperkit/blob/2f061e447e1435cdf1b9eda364cea6414f2c606b/src/lib/pci_virtio_block.c#L316
- https://securitylab.github.com/advisories/GHSL-2021-058-moby-hyperkit/

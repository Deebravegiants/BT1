# [M] CVE-2021-32843

## Summary
Severity: Medium
Advisory: CVE-2021-32843
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-17
Source: https://osv.dev/vulnerability/CVE-2021-32843
Type: osv

## Details
HyperKit is a toolkit for embedding hypervisor capabilities in an application. In versions 0.20210107 and prior of HyperKit, `virtio.c` has is a call to `vc_cfgread` that does not check for null which when called makes the host crash. This issue may lead to a guest crashing the host causing a denial of service. This issue is fixed in commit df0e46c7dbfd81a957d85e449ba41b52f6f7beb4.

## References
- https://securitylab.github.com/advisories/GHSL-2021-054_057-moby-hyperkit/
- https://github.com/moby/hyperkit/commit/df0e46c7dbfd81a957d85e449ba41b52f6f7beb4
- https://github.com/moby/hyperkit/pull/313

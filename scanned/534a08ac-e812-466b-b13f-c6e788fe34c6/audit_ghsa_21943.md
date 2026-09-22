# [H] Link Following in Kata Runtime

## Summary
Severity: High
Advisory: GHSA-877x-32pm-p28x
CVE: CVE-2020-2026
CWE: CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-877x-32pm-p28x
Type: github-advisory

## Affected
- Go: `github.com/kata-containers/runtime` — affected >=0 <1.9.1
- Go: `github.com/kata-containers/runtime` — affected >=1.10.0 <1.10.6
- Go: `github.com/kata-containers/runtime` — affected >=1.11.0 <1.11.1

## Details
A malicious guest compromised before a container creation (e.g. a malicious guest image or a guest running multiple containers) can trick the kata runtime into mounting the untrusted container filesystem on any host path, potentially allowing for code execution on the host. This issue affects Kata Containers 1.11 versions earlier than 1.11.1; Kata Containers 1.10 versions earlier than 1.10.5; Kata Containers 1.9 and earlier versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2026
- https://github.com/kata-containers/runtime/issues/2712
- https://github.com/kata-containers/runtime/pull/2713
- https://github.com/kata-containers/runtime/releases/tag/1.10.5
- https://github.com/kata-containers/runtime/releases/tag/1.11.1
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2P7FHA4AF6Y6PAVJBTTQPUEHXZQUOF3P
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6JPBKAQBF3OR72N55GWM2TDYQP2OHK6H
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6W5MKF7HSAIL2AX2BX6RV4WWVGUIKVLS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NJAMOVB7DSOGX7J26QH5HZKU7GSSX2VU
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QNJHSSPCKUGJDVXXIXK2JUWCRJDQX7CE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XWACJQSMY5BVDMVTF3FBN7HZSOSFOG3Q

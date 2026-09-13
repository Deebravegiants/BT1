# [H] Path Traversal vulnerability in Kubevirt

## Summary
Severity: High
Advisory: CVE-2022-1798
Aliases: GHSA-qv98-3369-g364, GO-2022-1000
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:H)
Published: 2022-09-15
Source: https://osv.dev/vulnerability/CVE-2022-1798
Type: osv

## Details
A path traversal vulnerability in KubeVirt versions up to 0.56 (and 0.55.1) on all platforms allows a user able to configure the kubevirt to read arbitrary files on the host filesystem which are publicly readable or which are readable for UID 107 or GID 107. /proc/self/<> is not accessible.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1798.json
- https://github.com/kubevirt/kubevirt/security/advisories/GHSA-qv98-3369-g364
- https://nvd.nist.gov/vuln/detail/CVE-2022-1798

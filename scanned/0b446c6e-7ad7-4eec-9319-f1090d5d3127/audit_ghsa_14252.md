# [C] sjqzhang go-fastdfs vulnerable to path traversal

## Summary
Severity: Critical
Advisory: GHSA-xq3x-grrj-fj6x
CVE: CVE-2023-1800
CWE: CWE-22, CWE-24, CWE-434
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-02
Source: https://github.com/advisories/GHSA-xq3x-grrj-fj6x
Type: github-advisory

## Affected
- Go: `github.com/sjqzhang/go-fastdfs` — affected >=0 <1.4.5-0.20230408141131-61cbff5124c6

## Details
sjqzhang go-fastdfs up to 1.4.3 is vulnerable to path traversal in the function upload of the file `/group1/upload` of the component `File Upload Handler`. The attack may be launched remotely and the exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1800
- https://github.com/sjqzhang/go-fastdfs/commit/61cbff5124c61e292994099372b11c06cdb5b80b
- https://github.com/sjqzhang/go-fastdfs
- https://github.com/yangyanglo/ForCVE/blob/93a16663cd32a36d37d8a0f0102e1592254d0279/2023-0x05.md
- https://github.com/yangyanglo/ForCVE/blob/main/2023-0x05.md
- https://vuldb.com/?ctiid.224768
- https://vuldb.com/?id.224768

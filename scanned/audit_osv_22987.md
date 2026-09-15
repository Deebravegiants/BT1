# [M] Read one byte past a buffer when normalizing Unicode

## Summary
Severity: Medium
Advisory: CVE-2022-41916
Aliases: GHSA-mgqr-gvh6-23cx
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-15
Source: https://osv.dev/vulnerability/CVE-2022-41916
Type: osv

## Details
Heimdal is an implementation of ASN.1/DER, PKIX, and Kerberos. Versions prior to 7.7.1 are vulnerable to a denial of service vulnerability in Heimdal's PKI certificate validation library, affecting the KDC (via PKINIT) and kinit (via PKINIT), as well as any third-party applications using Heimdal's libhx509. Users should upgrade to Heimdal 7.7.1 or 7.8. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41916.json
- https://github.com/heimdal/heimdal/security/advisories/GHSA-mgqr-gvh6-23cx
- https://nvd.nist.gov/vuln/detail/CVE-2022-41916
- https://security.gentoo.org/glsa/202310-06
- https://security.netapp.com/advisory/ntap-20230216-0008/
- https://www.debian.org/security/2022/dsa-5287
- https://lists.debian.org/debian-lts-announce/2022/11/msg00034.html

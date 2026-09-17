# [H] BIT-node-2020-8265

## Summary
Severity: High
Advisory: BIT-node-2020-8265
Aliases: BIT-node-min-2020-8265, CVE-2020-8265
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-node-2020-8265
Type: osv

## Affected
- Bitnami: `node` — affected >=15.0.0 <15.5.1

## Details
Node.js versions before 10.23.1, 12.20.1, 14.15.4, 15.5.1 are vulnerable to a use-after-free bug in its TLS implementation. When writing to a TLS enabled socket, node::StreamBase::Write calls node::TLSWrap::DoWrite with a freshly allocated WriteWrap object as first argument. If the DoWrite method does not return an error, this object is passed back to the caller as part of a StreamWriteResult structure. This may be exploited to corrupt memory leading to a Denial of Service or potentially other exploits.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://hackerone.com/reports/988103
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/H472D5HPXN6RRXCNFML3BK5OYC52CXF2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K4I6MZNC7C7VIDQR267OL4TVCI3ZKAC4/
- https://nodejs.org/en/blog/vulnerability/january-2021-security-releases/
- https://security.gentoo.org/glsa/202101-07
- https://security.netapp.com/advisory/ntap-20210212-0003/
- https://www.debian.org/security/2021/dsa-4826
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-8265

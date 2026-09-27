# [H] Memory exhaustion in routinator

## Summary
Severity: High
Advisory: GHSA-6mv9-qcx2-3hh3
CVE: CVE-2021-43174
CWE: CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-11-11
Source: https://github.com/advisories/GHSA-6mv9-qcx2-3hh3
Type: github-advisory

## Affected
- crates.io: `routinator` — affected >=0.9.0 <0.10.2

## Details
NLnet Labs Routinator versions 0.9.0 up to and including 0.10.1, support the gzip transfer encoding when querying RRDP repositories. This encoding can be used by an RRDP repository to cause an out-of-memory crash in these versions of Routinator. RRDP uses XML which allows arbitrary amounts of white space in the encoded data. The gzip scheme compresses such white space extremely well, leading to very small compressed files that become huge when being decompressed for further processing, big enough that Routinator runs out of memory when parsing input data waiting for the next XML element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43174
- https://github.com/NLnetLabs/routinator
- https://www.debian.org/security/2022/dsa-5041
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2021-43172_CVE-2021-43173_CVE-2021-43174.txt

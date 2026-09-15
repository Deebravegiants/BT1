# [H] HPACK Denial of Service vulnerability (HPACK Bomb)

## Summary
Severity: High
Advisory: GHSA-ffq8-576r-v26g
CVE: CVE-2016-6581
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-ffq8-576r-v26g
Type: github-advisory

## Affected
- PyPI: `hpack` — affected >=1.0.0 <2.3.0

## Details
A HTTP/2 implementation built using any version of the Python HPACK library between v1.0.0 and v2.2.0 could be targeted for a denial of service attack, specifically a so-called "HPACK Bomb" attack. This attack occurs when an attacker inserts a header field that is exactly the size of the HPACK dynamic header table into the dynamic header table. The attacker can then send a header block that is simply repeated requests to expand that field in the dynamic table. This can lead to a gigantic compression ratio of 4,096 or better, meaning that 16kB of data can decompress to 64MB of data on the target machine.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-6581
- https://github.com/advisories/GHSA-ffq8-576r-v26g
- https://github.com/pypa/advisory-database/tree/main/vulns/hpack/PYSEC-2017-87.yaml
- https://github.com/python-hyper/hpack
- https://python-hyper.org/hpack/en/latest/security/CVE-2016-6581.html
- https://web.archive.org/web/20200227233559/http://www.securityfocus.com/bid/92315
- http://python-hyper.org/projects/hpack/en/stable/security/CVE-2016-6581.html

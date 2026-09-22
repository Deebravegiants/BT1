# [H] Elixir can leak information due to weak use of crypto

## Summary
Severity: High
Advisory: GHSA-vfcg-5ggc-3rxx
CVE: CVE-2012-2146
CWE: CWE-327
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-vfcg-5ggc-3rxx
Type: github-advisory

## Affected
- PyPI: `Elixir` — affected >=0

## Details
Elixir prior to and including 0.7.1 uses Blowfish in CFB mode without constructing a unique initialization vector (IV), which makes it easier for context-dependent users to obtain sensitive information and decrypt the database. A patch has been [attached](https://sochotni.fedorapeople.org/python-elixir-aes-encryption-addition.patch) to the initial advisory to mitigate this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-2146
- https://bugzilla.redhat.com/show_bug.cgi?id=810013
- https://github.com/pypa/advisory-database/tree/main/vulns/elixir/PYSEC-2012-13.yaml
- http://elixir.ematia.de/trac/ticket/119
- http://groups.google.com/group/sqlelixir/browse_thread/thread/efc16227514cffa?pli=1
- http://www.openwall.com/lists/oss-security/2012/04/27/8
- http://www.openwall.com/lists/oss-security/2012/04/28/2
- http://www.openwall.com/lists/oss-security/2012/04/29/1

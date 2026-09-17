# [H] Improper hashing in enrocrypt

## Summary
Severity: High
Advisory: GHSA-35m5-8cvj-8783
CVE: CVE-2021-39182
CWE: CWE-326, CWE-327, CWE-328, CWE-916
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-35m5-8cvj-8783
Type: github-advisory

## Affected
- PyPI: `enrocrypt` — affected >=0 <1.1.4

## Details
### Impact
The vulnerability is we used MD5 hashing Algorithm In our hashing file. If anyone who is a beginner(and doesn't know about hashes)  can face problems as MD5 is considered a Insecure Hashing Algorithm. 

### Patches
The vulnerability is patched in v1.1.4 of the product, the users can upgrade to version 1.1.4.

### Workarounds
If u specifically want a version and don't want to upgrade, you can remove the `MD5` hashing function from the file `hashing.py` and this vulnerability will be gone

### References
https://www.cybersecurity-help.cz/vdb/cwe/916/
https://www.cybersecurity-help.cz/vdb/cwe/327/
https://www.cybersecurity-help.cz/vdb/cwe/328/
https://www.section.io/engineering-education/what-is-md5/
https://www.johndcook.com/blog/2019/01/24/reversing-an-md5-hash/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [**Enrocrypt's Official Repo**](http://www.github.com/Morgan-Phoenix/EnroCrypt)
* Create a Discussion in  [**Enrocrypt's Official Repo**](http://www.github.com/Morgan-Phoenix/EnroCrypt)

## References
- https://github.com/Morgan-Phoenix/EnroCrypt/security/advisories/GHSA-35m5-8cvj-8783
- https://nvd.nist.gov/vuln/detail/CVE-2021-39182
- https://github.com/Morgan-Phoenix/EnroCrypt/commit/e652d56ac60eadfc26489ab83927af13a9b9d8ce
- https://github.com/Morgan-Phoenix/EnroCrypt
- https://github.com/pypa/advisory-database/tree/main/vulns/enrocrypt/PYSEC-2021-385.yaml

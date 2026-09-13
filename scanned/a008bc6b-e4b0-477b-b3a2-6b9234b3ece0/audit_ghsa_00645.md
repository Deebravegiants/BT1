# [H] RSA weakness in tslite-ng

## Summary
Severity: High
Advisory: GHSA-wvcv-832q-fjg7
CVE: CVE-2020-26263
CWE: CWE-326
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-12-21
Source: https://github.com/advisories/GHSA-wvcv-832q-fjg7
Type: github-advisory

## Affected
- PyPI: `tlslite-ng` — affected >=0 <0.7.6

## Details
### Impact
The code that performs decryption and padding check in RSA PKCS#1 v1.5 decryption is data dependant.
In particular, code in current (as of 0.8.0-alpha38) master
https://github.com/tlsfuzzer/tlslite-ng/blob/0812ed60860fa61a6573b2c0e18771414958f46d/tlslite/utils/rsakey.py#L407-L441
and code in 0.7.5 branch
https://github.com/tlsfuzzer/tlslite-ng/blob/acdde3161124d6ae37c506b3476aea9996d12e97/tlslite/utils/rsakey.py#L394-L425
has multiple ways in which it leaks information (for one, it aborts as soon as the plaintext doesn't start with 0x00, 0x02) about the decrypted ciphertext (both the bit length of the decrypted message as well as where the first unexpected byte lays).

All TLS servers that enable RSA key exchange as well as applications that use the RSA decryption API directly are vulnerable.

All previous versions of tlslite-ng are vulnerable.

### Patches
The patches to fix it are proposed in 
https://github.com/tlsfuzzer/tlslite-ng/pull/438
https://github.com/tlsfuzzer/tlslite-ng/pull/439

Note: the patches depend on Python processing the individual bytes in side-channel free manner, this is known to not be the case: https://securitypitfalls.wordpress.com/2018/08/03/constant-time-compare-in-python/
As such, users that require side-channel resistance are recommended to use different TLS implementations, as stated in the [security policy](https://github.com/tlsfuzzer/tlslite-ng/blob/master/SECURITY.md) of tlslite-ng.

### Workarounds
There is no way to workaround this issue.

### References
https://securitypitfalls.wordpress.com/2018/08/03/constant-time-compare-in-python/

### For more information
If you have any questions or comments about this advisory please open an issue in [tlslite-ng](https://github.com/tlsfuzzer/tlslite-ng/issues).

## References
- https://github.com/tlsfuzzer/tlslite-ng/security/advisories/GHSA-wvcv-832q-fjg7
- https://nvd.nist.gov/vuln/detail/CVE-2020-26263
- https://github.com/tlsfuzzer/tlslite-ng/pull/438
- https://github.com/tlsfuzzer/tlslite-ng/pull/439
- https://github.com/tlsfuzzer/tlslite-ng/commit/c28d6d387bba59d8bd5cb3ba15edc42edf54b368
- https://github.com/pypa/advisory-database/tree/main/vulns/tlslite-ng/PYSEC-2020-143.yaml
- https://github.com/tlsfuzzer/tlslite-ng
- https://pypi.org/project/tlslite-ng
- https://securitypitfalls.wordpress.com/2018/08/03/constant-time-compare-in-python

# [H] ecdsa Denial of Service vulnerability in signature verification and signature malleability

## Summary
Severity: High
Advisory: GHSA-pwfw-mgfj-7g3g
CVE: CVE-2019-14853
CWE: CWE-391, CWE-755
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-10-08
Source: https://github.com/advisories/GHSA-pwfw-mgfj-7g3g
Type: github-advisory

## Affected
- PyPI: `ecdsa` — affected >=0 <0.13.3

## Details
## possible DoS in signature verification and signature malleability 

### Impact
Code using `VerifyingKey.verify()` and `VerifyingKey.verify_digest()` may receive exceptions other than the documented `BadSignatureError` when signatures are malformed. If those other exceptions are not caught, they may lead to program termination and thus Denial of Service

Code using `VerifyingKey.verify()` and `VerifyingKey.verify_digest()` with `sigdecode` option using `ecdsa.util.sigdecode_der` will accept signatures even if they are not properly formatted DER. This makes the signatures malleable. It impacts only applications that later sign the signatures or verify signatures of signatures, e.g. Bitcoin.

All versions between 0.5 and 0.13.2 (inclusive) are thought to be vulnerable. Code before 0.5 may be vulnerable but didn't receive extended analysis to rule this issue out.

### Patches
The patches have been merged to `master` branch in https://github.com/warner/python-ecdsa/pull/115.
The backported patches for a release in the 0.13 branch are in https://github.com/warner/python-ecdsa/pull/124

They are part of the 0.13.3 release.

There are no plans to backport them to earlier releases.

### Workarounds
It may be possible to prevent the Denial of Service by catching also `UnexpectedDER`, `IndexError` and `AssertionError` exceptions. That list hasn't been verified to be complete though. If those exceptions are raised, the signature verification process should consider the signature to be invalid.

To remediate signature malleability and the Denial of Service vulnerability, it may be possible to first verify that the signature is properly DER formatted ECDSA-Sig-Value, as defined in [RFC3279](https://tools.ietf.org/html/rfc3279), before passing it to `verify()` or `verify_digest()` methods. If the signature is determined to not follow the DER or encode a different structure, the signature verification process should consider the signature to be invalid.

### References
https://en.bitcoinwiki.org/wiki/Transaction_Malleability

### For more information
If you have any questions or comments about this advisory please open an issue in [python-ecdsa](https://github.com/warner/python-ecdsa/issues) project.

## References
- https://github.com/warner/python-ecdsa/security/advisories/GHSA-pwfw-mgfj-7g3g
- https://nvd.nist.gov/vuln/detail/CVE-2019-14853
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-14853
- https://github.com/pypa/advisory-database/tree/main/vulns/ecdsa/PYSEC-2019-177.yaml
- https://github.com/warner/python-ecdsa
- https://github.com/warner/python-ecdsa/releases/tag/python-ecdsa-0.13.3
- https://seclists.org/bugtraq/2019/Dec/33
- https://www.debian.org/security/2019/dsa-4588

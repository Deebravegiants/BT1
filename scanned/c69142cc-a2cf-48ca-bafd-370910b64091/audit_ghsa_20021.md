# [H] Denial of service by double-checked locking in openssl-src

## Summary
Severity: High
Advisory: GHSA-vr8j-hgmm-jh9r
CVE: CVE-2022-3996
CWE: CWE-667
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-vr8j-hgmm-jh9r
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=300.0.0 <300.0.12

## Details
If an X.509 certificate contains a malformed policy constraint and policy processing is enabled, then a write lock will be taken twice recursively. On some operating systems (most widely: Windows) this results in a denial of service when the affected process hangs. Policy processing being enabled on a publicly facing server is not considered to be a common setup. Policy processing is enabled by passing the `-policy' argument to the command line utilities or by calling either `X509_VERIFY_PARAM_add0_policy()' or `X509_VERIFY_PARAM_set1_policies()' functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3996
- https://github.com/openssl/openssl/commit/7725e7bfe6f2ce8146b6552b44e0d226be7638e7
- https://github.com/alexcrichton/openssl-src-rs
- https://www.openssl.org/news/secadv/20221213.txt

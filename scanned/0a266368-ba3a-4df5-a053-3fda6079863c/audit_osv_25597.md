# [M] uthenticode EKU validation bypass

## Summary
Severity: Medium
Advisory: CVE-2023-40012
Aliases: GHSA-gm2f-j4rj-6xqj
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-08-09
Source: https://osv.dev/vulnerability/CVE-2023-40012
Type: osv

## Details
uthenticode is a small cross-platform library for partially verifying Authenticode digital signatures. Versions of uthenticode prior to the 2.x series did not check Extended Key Usages in certificates, in violation of the Authenticode X.509 certificate profile. As a result, a malicious user could produce a "signed" PE file that uthenticode would verify and consider valid using an X.509 certificate that isn't entitled to produce code signatures (e.g., a SSL certificate). By design, uthenticode does not perform full-chain validation. However, the absence of EKU validation was an unintended oversight. The 2.0.0 release series includes EKU checks. There are no workarounds to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40012.json
- https://github.com/trailofbits/uthenticode/security/advisories/GHSA-gm2f-j4rj-6xqj
- https://nvd.nist.gov/vuln/detail/CVE-2023-40012
- https://github.com/trailofbits/uthenticode/commit/caeb1eb62412605f71bd96ce9bb9420644b6db53
- https://github.com/trailofbits/uthenticode/pull/78

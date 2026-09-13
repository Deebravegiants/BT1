# [M] Yeti affected by a Potential Denial of Service due to the One Milion Unicode characters attack

## Summary
Severity: Medium
Advisory: CVE-2024-45412
Aliases: GHSA-cwwm-pq9x-2cxv
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-09-10
Source: https://osv.dev/vulnerability/CVE-2024-45412
Type: osv

## Details
Yeti bridges the gap between CTI and DFIR practitioners by providing a Forensics Intelligence platform and pipeline. Remote user-controlled data tags can reach a Unicode normalization with a compatibility form NFKD. Under Windows, such normalization is costly in resources and may lead to denial of service with attacks such as One Million Unicode payload. This can get worse with the use of special Unicode characters like U+2100 (℀), or U+2105 (℅) which could lead the payload size to be tripled. Versions prior to 2.1.11 are affected by this vulnerability. The patch is included in 2.1.11.

## References
- https://hackerone.com/reports/2258758
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45412.json
- https://github.com/yeti-platform/yeti/security/advisories/GHSA-cwwm-pq9x-2cxv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45412
- https://github.com/yeti-platform/yeti/commit/f1f0082e7c165f148ae95f4deeb2786404797a39

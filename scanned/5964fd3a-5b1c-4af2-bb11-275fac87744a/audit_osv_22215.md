# [H] Remote program execution with user interaction

## Summary
Severity: High
Advisory: CVE-2022-23597
Aliases: GHSA-mjrg-9f8r-h3m7
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-02-01
Source: https://osv.dev/vulnerability/CVE-2022-23597
Type: osv

## Details
Element Desktop is a Matrix client for desktop platforms with Element Web at its core. Element Desktop before 1.9.7 is vulnerable to a remote program execution bug with user interaction. The exploit is non-trivial and requires clicking on a malicious link, followed by another button click. To the best of our knowledge, the vulnerability has never been exploited in the wild. If you are using Element Desktop < 1.9.7, we recommend upgrading at your earliest convenience. If successfully exploited, the vulnerability allows an attacker to specify a file path of a binary on the victim's computer which then gets executed. Notably, the attacker does *not* have the ability to specify program arguments. However, in certain unspecified configurations, the attacker may be able to specify an URI instead of a file path which then gets handled using standard platform mechanisms. These may allow exploiting further vulnerabilities in those mechanisms, potentially leading to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23597.json
- https://github.com/vector-im/element-desktop/security/advisories/GHSA-mjrg-9f8r-h3m7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23597
- https://github.com/vector-im/element-desktop/commit/89b1e39b801655e595337708d4319ba4313feafa

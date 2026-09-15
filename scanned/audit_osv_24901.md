# [M] CVE-2023-28320

## Summary
Severity: Medium
Advisory: CVE-2023-28320
Aliases: CURL-CVE-2023-28320
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-28320
Type: osv

## Details
A denial of service vulnerability exists in curl <v8.1.0 in the way libcurl provides several different backends for resolving host names, selected at build time. If it is built to use the synchronous resolver, it allows name resolves to time-out slow operations using `alarm()` and `siglongjmp()`. When doing this, libcurl used a global buffer that was not mutex protected and a multi-threaded application might therefore crash or otherwise misbehave.

## References
- https://hackerone.com/reports/1929597
- https://support.apple.com/kb/HT213843
- https://support.apple.com/kb/HT213844
- https://support.apple.com/kb/HT213845
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28320.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28320
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230609-0009/
- http://seclists.org/fulldisclosure/2023/Jul/47
- http://seclists.org/fulldisclosure/2023/Jul/48
- http://seclists.org/fulldisclosure/2023/Jul/52

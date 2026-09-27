# [M] XZ has a heap-use-after-free bug in threaded .xz decoder

## Summary
Severity: Medium
Advisory: CVE-2025-31115
Aliases: GHSA-6cc8-p5mm-29w2, HSEC-2025-0003
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-03
Source: https://osv.dev/vulnerability/CVE-2025-31115
Type: osv

## Details
XZ Utils provide a general-purpose data-compression library plus command-line tools. In XZ Utils 5.3.3alpha to 5.8.0, the multithreaded .xz decoder in liblzma has a bug where invalid input can at least result in a crash. The effects include heap use after free and writing to an address based on the null pointer plus an offset. Applications and libraries that use the lzma_stream_decoder_mt function are affected. The bug has been fixed in XZ Utils 5.8.1, and the fix has been committed to the v5.4, v5.6, v5.8, and master branches in the xz Git repository. No new release packages will be made from the old stable branches, but a standalone patch is available that applies to all affected releases.

## References
- http://www.openwall.com/lists/oss-security/2025/04/03/1
- http://www.openwall.com/lists/oss-security/2025/04/03/2
- http://www.openwall.com/lists/oss-security/2025/04/03/3
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://tukaani.org/xz/xz-cve-2025-31115.patch
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31115.json
- https://github.com/tukaani-project/xz/security/advisories/GHSA-6cc8-p5mm-29w2
- https://nvd.nist.gov/vuln/detail/CVE-2025-31115
- https://github.com/tukaani-project/xz/commit/d5a2ffe41bb77b918a8c96084885d4dbe4bf6480

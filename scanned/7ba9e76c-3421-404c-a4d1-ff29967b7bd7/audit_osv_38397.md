# [M] osslsigncode has an Integer Underflow in PE Page Hash Calculation Can Cause Out-of-Bounds Read

## Summary
Severity: Medium
Advisory: CVE-2026-39855
Aliases: GHSA-76vv-x5rr-q3mr
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39855
Type: osv

## Details
osslsigncode is a tool that implements Authenticode signing and timestamping. Prior to 2.13, an integer underflow vulnerability exists in osslsigncode version 2.12 and earlier in the PE page-hash computation code (pe_page_hash_calc()). When page hash processing is performed on a PE file, the function subtracts hdrsize from pagesize without first validating that pagesize >= hdrsize. If a malicious PE file sets SizeOfHeaders (hdrsize) larger than SectionAlignment (pagesize), the subtraction underflows and produces a very large unsigned length. The code allocates a zero-filled buffer of pagesize bytes and then attempts to hash pagesize - hdrsize bytes from that buffer. After the underflow, this results in an out-of-bounds read from the heap and can crash the process. The vulnerability can be triggered while signing a malicious PE file with page hashing enabled (-ph), or while verifying a malicious signed PE file that already contains page hashes. Verification of an already signed file does not require the verifier to pass -ph. This vulnerability is fixed in 2.13.

## References
- https://github.com/mtrojnar/osslsigncode/releases/tag/2.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39855.json
- https://github.com/mtrojnar/osslsigncode/security/advisories/GHSA-76vv-x5rr-q3mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-39855
- https://github.com/mtrojnar/osslsigncode/commit/2a5409b7c4b6c6fad2b093531e8fea6cf08e1568

# [M] pyzipper has an encryption bypass for small files encrypted using it

## Summary
Severity: Medium
Advisory: GHSA-crqm-m339-7m2p
CVE: CVE-2026-44722
CWE: CWE-480
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-crqm-m339-7m2p
Type: github-advisory

## Affected
- PyPI: `pyzipper` — affected >=0 <0.4.0

## Details
### Impact
A Python operator precedence bug in pyzipper/zipfile_aes.py caused the AE-2 format to never be automatically selected during encryption, regardless of file size or compression type. As a result, all encrypted entries are written in AE-1 format unless AE-2 is explicitly forced by the caller. AE-1 stores the plaintext CRC32 checksum unencrypted in the ZIP header. During investigation of this issue, it was also found that when writing to an unseekable zip archive, the CRC32 value was always written to the datadescripter section.

The AES encryption itself is not broken. An attacker who possesses the archive can read the CRC32 from the header without decrypting anything, then brute-force candidate plaintexts by computing CRC32(candidate) and comparing against the stored value. In practice, this attack is feasible today only against small or low-entropy files, as CRC32 exhaustion across a large plaintext space is computationally prohibitive on current hardware. Files with high-entropy or large content are not practically at risk under current computing constraints. Without this bug, pyzipper would have removed the CRC32 value for any file with content of less than 20 bytes uncompressed.

### Patches
Upgrade to pyzipper 0.4.0 that changes the default behaviour of pyzipper to always use the AE-2 format and exclude the CRC32 values, unless instructed to do otherwise.

If rewriting the zip archive to remove the CRC values for small files, the entire zip archive should be recreated to avoid the original local file header with the CRC included remaining in the zip file in a detached state.

## Credit
Thanks to Lucas Lavarello from Kulkan Security for identifying this issue.

### References
https://www.winzip.com/en/support/aes-encryption/#CRC
https://www.winzip.com/en/support/aes-encryption/#crc-faq

## References
- https://github.com/danifus/pyzipper/security/advisories/GHSA-crqm-m339-7m2p
- https://github.com/danifus/pyzipper
- https://github.com/danifus/pyzipper/releases/tag/v0.4.0

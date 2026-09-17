# [H] CVE-2021-3674

## Summary
Severity: High
Advisory: CVE-2021-3674
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-03-24
Source: https://osv.dev/vulnerability/CVE-2021-3674
Type: osv

## Details
A flaw was found in rizin. The create_section_from_phdr function allocates space for ELF section data by processing the headers. Crafted values in the headers can cause out of bounds reads, which can lead to memory corruption and possibly code execution through the binary object's callback function.

## References
- https://github.com/rizinorg/rizin/pull/1313
- https://gist.github.com/netspooky/61101e191afee95feda7dbd2f6b061c4

# [H] CVE-2024-42381

## Summary
Severity: High
Advisory: CVE-2024-42381
CVSS: 8.3 (CVSS:3.1/AC:H/AV:N/A:H/C:H/I:H/PR:N/S:C/UI:R)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-42381
Type: osv

## Details
os/linux/elf.rb in Homebrew brew before 4.2.20 uses ldd to load ELF files obtained from untrusted sources, which allows attackers to achieve code execution via an ELF file with a custom .interp section. NOTE: this code execution would occur during an un-sandboxed binary relocation phase, which occurs before a user would expect execution of downloaded package content. (237d1e783f7ee261beaba7d3f6bde22da7148b0a was the tested vulnerable version.)

## References
- https://brew.sh/2024/07/30/homebrew-security-audit/
- https://github.com/Homebrew/brew/releases/tag/4.2.20
- https://github.com/Homebrew/brew/tree/237d1e783f7ee261beaba7d3f6bde22da7148b0a
- https://github.com/trailofbits/publications/blob/master/reviews/2023-08-28-homebrew-securityreview.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42381.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42381
- https://github.com/Homebrew/brew/commit/916b37388d3851a8a93a8e9b4adc38873680ead7
- https://github.com/Homebrew/brew/pull/17136
- https://blog.trailofbits.com/2024/07/30/our-audit-of-homebrew/

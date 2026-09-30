# [H] CVE-2024-24479

## Summary
Severity: High
Advisory: CVE-2024-24479
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-21
Source: https://osv.dev/vulnerability/CVE-2024-24479
Type: osv

## Details
A Buffer Overflow in Wireshark before 4.2.0 allows a remote attacker to cause a denial of service via the wsutil/to_str.c, and format_fractional_part_nsecs components. NOTE: this is disputed by the vendor because neither release 4.2.0 nor any other release was affected.

## References
- https://gist.github.com/1047524396/c50ad17e9a1a18990043a7cd27814c78
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZT2BX7UARZVVWKITSZMHW7BHXGIKRSR2/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24479.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZT2BX7UARZVVWKITSZMHW7BHXGIKRSR2/
- https://nvd.nist.gov/vuln/detail/CVE-2024-24479
- https://github.com/wireshark/wireshark/commit/c3720cff158c265dec2a0c6104b1d65954ae6bfd

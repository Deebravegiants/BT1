# [M] CVE-2021-3696

## Summary
Severity: Medium
Advisory: CVE-2021-3696
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-07-06
Source: https://osv.dev/vulnerability/CVE-2021-3696
Type: osv

## Details
A heap out-of-bounds write may heppen during the handling of Huffman tables in the PNG reader. This may lead to data corruption in the heap space. Confidentiality, Integrity and Availablity impact may be considered Low as it's very complex to an attacker control the encoding and positioning of corrupted Huffman entries to achieve results such as arbitrary code execution and/or secure boot circumvention. This flaw affects grub2 versions prior grub-2.12.

## References
- https://security.gentoo.org/glsa/202209-12
- https://security.netapp.com/advisory/ntap-20220930-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1991686

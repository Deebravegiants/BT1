# [M] CVE-2017-6851

## Summary
Severity: Medium
Advisory: CVE-2017-6851
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6851
Type: osv

## Details
The jas_matrix_bindsub function in jas_seq.c in JasPer 2.0.10 allows remote attackers to cause a denial of service (invalid read) via a crafted image.

## References
- https://blogs.gentoo.org/ago/2017/01/25/jasper-invalid-memory-read-in-jas_matrix_bindsub-jas_seq-c/
- https://security.gentoo.org/glsa/201908-03
- https://github.com/mdadams/jasper/issues/113

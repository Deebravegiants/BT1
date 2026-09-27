# [H] CVE-2022-4904

## Summary
Severity: High
Advisory: CVE-2022-4904
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-03-06
Source: https://osv.dev/vulnerability/CVE-2022-4904
Type: osv

## Details
A flaw was found in the c-ares package. The ares_set_sortlist is missing checks about the validity of the input string, which allows a possible arbitrary length stack overflow. This issue may cause a denial of service or a limited impact on confidentiality and integrity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4904.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/33LDNS6RPOPP36Z4MPWXALUQZXJCWJS2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-4904
- https://security.gentoo.org/glsa/202401-02
- https://bugzilla.redhat.com/show_bug.cgi?id=2168631
- https://github.com/c-ares/c-ares/issues/496

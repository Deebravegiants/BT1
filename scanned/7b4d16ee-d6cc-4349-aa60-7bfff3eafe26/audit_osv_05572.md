# [M] BIT-golang-2021-27919

## Summary
Severity: Medium
Advisory: BIT-golang-2021-27919
Aliases: CVE-2021-27919, GO-2021-0067
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-golang-2021-27919
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.16.0 <1.16.1

## Details
archive/zip in Go 1.16.x before 1.16.1 allows attackers to cause a denial of service (panic) upon attempted use of the Reader.Open API for a ZIP archive in which ../ occurs at the beginning of any filename.

## References
- https://groups.google.com/g/golang-announce/c/MfiLYjG-RAw
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2MU47VKTNXX33ZDLTI2ORRUY3KLJKU6G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HM7U5JNS5WU66Q3S26PFIU2ITB2ATTQ4/
- https://security.gentoo.org/glsa/202208-02
- https://nvd.nist.gov/vuln/detail/CVE-2021-27919

# [M] gopeak MasterLab User.php base64ImageContent unrestricted upload

## Summary
Severity: Medium
Advisory: CVE-2023-7147
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-29
Source: https://osv.dev/vulnerability/CVE-2023-7147
Type: osv

## Details
A vulnerability, which was classified as critical, was found in gopeak MasterLab up to 3.3.10. Affected is the function base64ImageContent of the file app/ctrl/User.php. The manipulation of the argument image leads to unrestricted upload. It is possible to launch the attack remotely. VDB-249150 is the identifier assigned to this vulnerability.

## References
- https://note.zhaoj.in/share/affd8cjn50HC
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7147.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-7147
- https://vuldb.com/?id.249150
- https://vuldb.com/?ctiid.249150

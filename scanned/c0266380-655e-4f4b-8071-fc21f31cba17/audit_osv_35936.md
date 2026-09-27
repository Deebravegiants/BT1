# [M] Velociraptor Multiple Crashes in NTFS Parser when applied to invalid NTFS Volumes

## Summary
Severity: Medium
Advisory: CVE-2026-17535
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-17535
Type: osv

## Details
Velociraptor's NTFS parsing library mishandles several out of bound and memory exhaustion bugs which may be triggered by maliciously crafted NTFS images.

Typically Velociraptor's NTFS parser is used on live NTFS filesystems, limiting the opportunity of attackers corrupting the filesystem. However, in some applications (e.g.  dead disk forensics https://docs.velociraptor.app/docs/forensic/deaddisk/ ) Velociraptor may be used on untrusted NTFS image files. 

If an attacker is able to inject maliciously corrupted NTFS Volumes they can cause a crash and a Denial of Service.

## References
- https://github.com/Velocidex/velociraptor/
- http://docs.velociraptor.app/announcements/advisories/cve-2026-17535/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17535.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17535

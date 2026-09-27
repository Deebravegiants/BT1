# [M] CVE-2023-3592

## Summary
Severity: Medium
Advisory: CVE-2023-3592
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2023-10-02
Source: https://osv.dev/vulnerability/CVE-2023-3592
Type: osv

## Details
In Mosquitto before 2.0.16, a memory leak occurs when clients send v5 CONNECT packets with a will message that contains invalid property types.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3592.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3592
- https://security.gentoo.org/glsa/202401-09
- https://mosquitto.org/blog/2023/08/version-2-0-16-released/

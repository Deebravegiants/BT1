# [C] CVE-2024-38441

## Summary
Severity: Critical
Advisory: CVE-2024-38441
Aliases: GHSA-mj6v-cr68-mj9q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-16
Source: https://osv.dev/vulnerability/CVE-2024-38441
Type: osv

## Details
Netatalk before 3.2.1 has an off-by-one error and resultant heap-based buffer overflow because of setting ibuf[len] to '\0' in FPMapName in afp_mapname in etc/afpd/directory.c. 2.4.1 and 3.1.19 are also fixed versions.

## References
- https://github.com/Netatalk/netatalk/blob/90d91a9ac9a7d6132ab7620d31c8c23400949206/etc/afpd/directory.c#L2333
- https://lists.debian.org/debian-lts-announce/2024/11/msg00026.html
- https://netatalk.io/security/CVE-2024-38441
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38441.json
- https://github.com/Netatalk/netatalk/security/advisories/GHSA-mj6v-cr68-mj9q
- https://nvd.nist.gov/vuln/detail/CVE-2024-38441
- https://github.com/Netatalk/netatalk/issues/1098

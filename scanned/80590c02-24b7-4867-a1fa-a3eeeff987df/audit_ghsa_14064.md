# [M] Minio console object names with RIGHT-TO-LEFT OVERRIDE unicode character can be exploited

## Summary
Severity: Medium
Advisory: GHSA-jv3f-7m33-qp65
CVE: CVE-2023-33955
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-jv3f-7m33-qp65
Type: github-advisory

## Affected
- Go: `github.com/minio/console` — affected >=0 <0.28.0

## Details
### Impact
Unicode RIGHT-TO-LEFT OVERRIDE characters can be used to mask the original filename.

### Reported-By
Thanks to the report from Mio Li [wulilixi1@gmail.com](mailto:wulilixi1@gmail.com)

### Patches
```
commit 17e791afb90c9ad27c65f63c6be14f2f6a3a9d60
Author: Daniel Valdivia <18384552+dvaldivia@users.noreply.github.com>
Date:   Tue May 23 08:47:12 2023 -0700

    Replace RIGHT-TO-LEFT OVERRIDE unicode (#2828)
    
    Signed-off-by: Daniel Valdivia <18384552+dvaldivia@users.noreply.github.com>
```

### Workarounds
Workarounds are to remove the concerned file and rewrite it properly with the right file and extensions.  Avoid using RTLO characters in your filenames.

## References
- https://github.com/minio/console/security/advisories/GHSA-jv3f-7m33-qp65
- https://nvd.nist.gov/vuln/detail/CVE-2023-33955
- https://github.com/minio/console/commit/17e791afb90c9ad27c65f63c6be14f2f6a3a9d60
- https://github.com/minio/console
- https://github.com/minio/console/releases/tag/v0.28.0

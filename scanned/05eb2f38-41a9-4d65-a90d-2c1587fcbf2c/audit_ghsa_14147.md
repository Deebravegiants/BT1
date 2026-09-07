# [C] Wings vulnerable to escape to host from installation container

## Summary
Severity: Critical
Advisory: GHSA-p744-4q6p-hvc2
CVE: CVE-2023-32080
CWE: CWE-250
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-p744-4q6p-hvc2
Type: github-advisory

## Affected
- Go: `github.com/pterodactyl/wings` — affected >=0 <1.7.5
- Go: `github.com/pterodactyl/wings` — affected >=1.11.0 <1.11.6

## Details
### Impact

This vulnerability impacts anyone running the affected versions of Wings.  This vulnerability can be used to gain access to the host system running Wings if a user is able to modify an server's install script or the install script executes code supplied by the user (either through environment variables, or commands that execute commands based off of user data).

### Patches

This vulnerability has been resolved in version `v1.11.6` of Wings, and has been back-ported to the 1.7 release series in `v1.7.5`.

Anyone running `v1.11.x` should upgrade to `v1.11.6` and anyone running `v1.7.x` should upgrade to `v1.7.5`.

### Workarounds

Running Wings with a rootless container runtime may mitigate the severity of any attacks, however the majority of users are using container runtimes that run as root as per our documentation.

SELinux may prevent attackers from performing certain operations against the host system, however privileged containers have a lot of freedom even on systems with SELinux enabled.

TL;DR: None at this time.

### Extra details

It should be noted that this was a known attack vector, for attackers to easily exploit this attack it would require compromising an administrator account on a Panel.  However, certain eggs (the data structure that holds the install scripts that get passed to Wings) have an issue where they are unknowingly executing shell commands with escalated privileges provided by untrusted user data.

## References
- https://github.com/pterodactyl/wings/security/advisories/GHSA-p744-4q6p-hvc2
- https://nvd.nist.gov/vuln/detail/CVE-2023-32080
- https://github.com/pterodactyl/wings
- https://github.com/pterodactyl/wings/releases/tag/v1.11.6
- https://github.com/pterodactyl/wings/releases/tag/v1.17.5
- https://github.com/pterodactyl/wings/releases/tag/v1.7.5

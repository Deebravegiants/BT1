# [H] October/System authenticated file write leads to remote code execution

## Summary
Severity: High
Advisory: GHSA-wv23-pfj7-2mjj
CVE: CVE-2021-32649
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-wv23-pfj7-2mjj
Type: github-advisory

## Affected
- Packagist: `october/system` — affected >=1.1.0 <1.1.6
- Packagist: `october/system` — affected >=0 <1.0.473

## Details
### Impact

Assuming an attacker with "create, modify and delete website pages" privileges in the backend is able to execute PHP code by running specially crafted Twig code in the template markup.

### Patches

Issue has been patched in Build 473 and v1.1.6

### Workarounds

Apply https://github.com/octobercms/october/commit/167b592eed291ae1563c8fcc5b9b34a03a300f26 to your installation manually if you are unable to upgrade.

### References

Credits to:
• David Miller

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

## References
- https://github.com/octobercms/october/security/advisories/GHSA-wv23-pfj7-2mjj
- https://nvd.nist.gov/vuln/detail/CVE-2021-32649
- https://github.com/octobercms/october/commit/167b592eed291ae1563c8fcc5b9b34a03a300f26
- https://github.com/octobercms/october

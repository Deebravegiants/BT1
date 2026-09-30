# [H] Local File Inclusion by unauthenticated users

## Summary
Severity: High
Advisory: GHSA-xwjr-6fj7-fc6h
CVE: CVE-2020-15246
CWE: CWE-22, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-11-23
Source: https://github.com/advisories/GHSA-xwjr-6fj7-fc6h
Type: github-advisory

## Affected
- Packagist: `october/cms` — affected >=1.0.421 <1.0.469

## Details
### Impact
An attacker can exploit this vulnerability to read local files on an October CMS server. The vulnerability is exploitable by unauthenticated users via a specially crafted request.

### Patches
Issue has been patched in Build 469 (v1.0.469) and v1.1.0.

### Workarounds
Apply https://github.com/octobercms/library/commit/80aab47f044a2660aa352450f55137598f362aa4 to your installation manually if unable to upgrade to Build 469.

### References
Reported by [ka1n4t](https://github.com/ka1n4t)

### For more information
If you have any questions or comments about this advisory:
* Email us at [hello@octobercms.com](mailto:hello@octobercms.com)

### Threat assessment:
<img width="1105" alt="Screen Shot 2020-10-10 at 1 05 19 PM" src="https://user-images.githubusercontent.com/7253840/95663086-4ffc4780-0af9-11eb-9bb6-fd40cf11c033.png">

## References
- https://github.com/octobercms/october/security/advisories/GHSA-xwjr-6fj7-fc6h
- https://nvd.nist.gov/vuln/detail/CVE-2020-15246
- https://github.com/octobercms/library/commit/80aab47f044a2660aa352450f55137598f362aa4
- https://github.com/octobercms/october

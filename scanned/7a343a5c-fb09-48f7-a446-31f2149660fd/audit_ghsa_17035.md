# [M] 1Panel open source panel project has an unauthorized vulnerability.

## Summary
Severity: Medium
Advisory: GHSA-26w3-q4j8-4xjp
CVE: CVE-2024-27288
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-26w3-q4j8-4xjp
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=0 <1.10.1-lts

## Details
### Impact

The steps are as follows:

1. Access https://IP:PORT/ in the browser, which prompts the user to access with a secure entry point.
![image](https://github.com/1Panel-dev/1Panel/assets/46734380/8dc7d81c-6cc3-4b5d-a1d4-d3c5ed2de005)

2. Use Burp to intercept:
![image](https://github.com/1Panel-dev/1Panel/assets/46734380/f8e93d08-1b66-4434-8923-2e8e3dedebe3)

When opening the browser and entering the URL (allowing the first intercepted packet through Burp), the following is displayed:
![image](https://github.com/1Panel-dev/1Panel/assets/46734380/118c0102-7c89-404d-834a-88a644482afc)

It is found that in this situation, we can access the console page (although no data is returned and no modification operations can be performed)."

Affected versions: <= 1.10.0-lts

### Patches

The vulnerability has been fixed in v1.10.1-lts.

### Workarounds

It is recommended to upgrade the version to 1.10.1-lts.

### References

If you have any questions or comments about this advisory:

Open an issue in https://github.com/1Panel-dev/1Panel
Email us at wanghe@fit2cloud.com

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-26w3-q4j8-4xjp
- https://nvd.nist.gov/vuln/detail/CVE-2024-27288
- https://github.com/1Panel-dev/1Panel/pull/4014
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v1.10.1-lts

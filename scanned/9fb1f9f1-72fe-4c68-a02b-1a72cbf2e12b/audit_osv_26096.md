# [H] Insufficient boundary checks for DIO and DAO messages in RPL-Lite in Contiki-NG

## Summary
Severity: High
Advisory: CVE-2023-50927
Aliases: GHSA-9423-rgj4-wjfw
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-02-14
Source: https://osv.dev/vulnerability/CVE-2023-50927
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. An attacker can trigger out-of-bounds reads in the RPL-Lite implementation of the RPL protocol in the Contiki-NG operating system. This vulnerability is caused by insufficient control of the lengths for DIO and DAO messages, in particular when they contain RPL sub-option headers. The problem has been patched in Contiki-NG 4.9. Users are advised to upgrade. Users unable to upgrade should manually apply the code changes in PR #2484.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50927.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-9423-rgj4-wjfw
- https://nvd.nist.gov/vuln/detail/CVE-2023-50927
- https://github.com/contiki-ng/contiki-ng/pull/2484

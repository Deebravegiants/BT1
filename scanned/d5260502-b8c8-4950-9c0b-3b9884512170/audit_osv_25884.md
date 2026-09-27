# [H] lte-pic32-writer's sendto.txt may disclose URL and the API key

## Summary
Severity: High
Advisory: CVE-2023-46723
Aliases: GHSA-9qgg-ph2v-v4mh
CVSS: 8.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-46723
Type: osv

## Details
lte-pic32-writer is a writer for PIC32 devices. In versions 0.0.1 and prior, those who use `sendto.txt` are vulnerable to attackers who known the IMEI reading the sendto.txt. The sendto.txt file can contain the SNS(such as slack and zulip) URL and API key. As of time of publication, a patch is not yet available. As workarounds, avoid using `sendto.txt` or use `.htaccess` to block access to `sendto.txt`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46723.json
- https://github.com/paijp/lte-pic32-writer/security/advisories/GHSA-9qgg-ph2v-v4mh
- https://nvd.nist.gov/vuln/detail/CVE-2023-46723

# [H] Wazuh: Missing input validation in multiple active response scripts allows argument injection

## Summary
Severity: High
Advisory: CVE-2026-54085
Aliases: GHSA-mvh4-g699-984j
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-54085
Type: osv

## Details
Wazuh is an open-source security platform providing unified XDR and SIEM protection for endpoints and cloud workloads. In versions 4.2.0 through 4.14.6, multiple active response scripts pass attacker-influenced alert fields to privileged system commands without validating their format, allowing argument injection into tools that run as root. Five of the eight scripts that handle the srcip field, route-null.c, netsh.c, pf.c, npf.c, and ipfw.c, omit the get_ip_version() check that rejects non-IP input, and disable-account.c passes the dstuser field to passwd/chuser with only a comparison against "root". An attacker who can inject crafted log events, for example via syslog, can supply srcip or dstuser values that, when an active response rule triggers, are passed unvalidated to firewall and account-management commands such as pfctl, npfctl, ipfw, route, netsh, and passwd. This enables injecting additional command arguments, and on Windows the unquoted CreateProcess command-line concatenation in wpopenv() lets a srcip containing spaces add further arguments, while disable-account.c can be abused to lock arbitrary system accounts. This issue is fixed in version 4.14.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54085.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-mvh4-g699-984j
- https://nvd.nist.gov/vuln/detail/CVE-2026-54085
- https://github.com/wazuh/wazuh/commit/b7f3a5e59000e4cdef75f397f1107ae3e1c186a9

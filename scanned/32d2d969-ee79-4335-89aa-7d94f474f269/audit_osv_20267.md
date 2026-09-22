# [H] CVE-2021-32656

## Summary
Severity: High
Advisory: CVE-2021-32656
Aliases: GHSA-j875-vr2q-h6x6
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-32656
Type: osv

## Details
Nextcloud Server is a Nextcloud package that handles data storage. A vulnerability in federated share exists in versions prior to 19.0.11, 20.0.10, and 21.0.2. An attacker can gain access to basic information about users of a server by accessing a public link that a legitimate server user added as a federated share. This happens because Nextcloud supports sharing registered users with other Nextcloud servers, which can be done automatically when selecting the "Add server automatically once a federated share was created successfully" setting. The vulnerability is patched in versions 19.0.11, 20.0.10, and 21.0.2 As a workaround, disable "Add server automatically once a federated share was created successfully" in the Nextcloud settings.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-j875-vr2q-h6x6
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1167853

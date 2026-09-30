# [C] CVE-2018-1000666

## Summary
Severity: Critical
Advisory: CVE-2018-1000666
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000666
Type: osv

## Details
GIG Technology NV JumpScale Portal 7 version before commit 15443122ed2b1cbfd7bdefc048bf106f075becdb contains a CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection') vulnerability in method: notifySpaceModification; that can result in Improper validation of parameters results in command execution. This attack appear to be exploitable via Network connectivity, required minimal auth privileges (everyone can register an account). This vulnerability appears to have been fixed in After commit 15443122ed2b1cbfd7bdefc048bf106f075becdb.

## References
- https://medium.com/%40vrico315/vulnerability-in-jumpscale-portal-7-a88098a1caca
- https://github.com/0-complexity/openvcloud/issues/1207
- https://github.com/jumpscale7/jumpscale_portal/pull/108
- https://github.com/jumpscale7/jumpscale_portal/blob/c997bb1824862b08246d60e34e950df06ebac68c/apps/portalbase/system/system__contentmanager/methodclass/system_contentmanager.py#L293-L315
- https://telegra.ph/Description-of-vulnerability-in-JumpScale-Portal-7-08-23

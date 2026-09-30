# [M] CVE-2018-18509

## Summary
Severity: Medium
Advisory: CVE-2018-18509
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2018-18509
Type: osv

## Details
A flaw during verification of certain S/MIME signatures causes emails to be shown in Thunderbird as having a valid digital signature, even if the shown message contents aren't covered by the signature. The flaw allows an attacker to reuse a valid S/MIME signature to craft an email message with arbitrary content. This vulnerability affects Thunderbird < 60.5.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00043.html
- https://github.com/RUB-NDS/Johnny-You-Are-Fired/blob/master/paper/johnny-fired.pdf
- https://www.mozilla.org/security/advisories/mfsa2019-06/
- http://packetstormsecurity.com/files/152703/Johnny-You-Are-Fired.html
- http://seclists.org/fulldisclosure/2019/Apr/38
- https://access.redhat.com/errata/RHSA-2019:1144
- http://www.openwall.com/lists/oss-security/2019/04/30/4
- https://bugzilla.mozilla.org/show_bug.cgi?id=1507218
- https://github.com/RUB-NDS/Johnny-You-Are-Fired

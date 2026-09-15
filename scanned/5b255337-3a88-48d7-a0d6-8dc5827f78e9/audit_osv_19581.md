# [H] CVE-2021-22212

## Summary
Severity: High
Advisory: CVE-2021-22212
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-06-08
Source: https://osv.dev/vulnerability/CVE-2021-22212
Type: osv

## Details
ntpkeygen can generate keys that ntpd fails to parse. NTPsec 1.2.0 allows ntpkeygen to generate keys with '#' characters. ntpd then either pads, shortens the key, or fails to load these keys entirely, depending on the key type and the placement of the '#'. This results in the administrator not being able to use the keys as expected or the keys are shorter than expected and easier to brute-force, possibly resulting in MITM attacks between ntp clients and ntp servers. For short AES128 keys, ntpd generates a warning that it is padding them.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3GIT2HYL5BQXPGKI6ZDNG473IEQ5WQF2/
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-22212.json
- https://bugzilla.redhat.com/show_bug.cgi?id=1955859
- https://gitlab.com/NTPsec/ntpsec/-/issues/699

# [M] CVE-2021-20178

## Summary
Severity: Medium
Advisory: CVE-2021-20178
Aliases: GHSA-wv5p-gmmv-wh9v, PYSEC-2021-106
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-20178
Type: osv

## Details
A flaw was found in ansible module where credentials are disclosed in the console log by default and not protected by the security feature when using the bitbucket_pipeline_variable module. This flaw allows an attacker to steal bitbucket_pipeline credentials. The highest threat from this vulnerability is to confidentiality.

## References
- https://github.com/ansible/ansible/blob/v2.9.18/changelogs/CHANGELOG-v2.9.rst#security-fixes%2C
- https://lists.debian.org/debian-lts-announce/2023/12/msg00018.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FUQ2QKAQA5OW2TY3ACZZMFIAJ2EQTG37/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HIU7QZUV73U6ZQ65VJWSFBTCALVXLH55/
- https://bugzilla.redhat.com/show_bug.cgi?id=1914774
- https://github.com/ansible-collections/community.general/pull/1635%2C

# [H] CVE-2017-18265

## Summary
Severity: High
Advisory: CVE-2017-18265
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-09
Source: https://osv.dev/vulnerability/CVE-2017-18265
Type: osv

## Details
Prosody before 0.10.0 allows remote attackers to cause a denial of service (application crash), related to an incompatibility with certain versions of the LuaSocket library, such as the lua-socket package from Debian stretch. The attacker needs to trigger a stream error. A crash can be observed in, for example, the c2s module.

## References
- https://prosody.im/issues/issue/987
- https://bugs.debian.org/875829
- https://hg.prosody.im/0.9/rev/adfffc5b4e2a
- https://hg.prosody.im/0.9/rev/176b7f4e4ac9
- https://www.debian.org/security/2018/dsa-4198

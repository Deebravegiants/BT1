# [C] CVE-2020-24133

## Summary
Severity: Critical
Advisory: CVE-2020-24133
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-07-14
Source: https://osv.dev/vulnerability/CVE-2020-24133
Type: osv

## Details
A heap buffer overflow vulnerability in the r_asm_swf_disass function of Radare2-extras before commit e74a93c allows attackers to execute arbitrary code or carry out denial of service (DOS) attacks.

## References
- https://github.com/radareorg/radare2-extras/pull/255
- https://github.com/radareorg/radare2-extras/pull/255/commits/4a8b24475549ff10bdf6d07fd4b5f6c1cc6246ea
- https://github.com/radareorg/radare2-extras/pull/255/commits/9f6a221433964d9b14f3ed78bc9fb059395b893b
- https://cwe.mitre.org/data/definitions/122.html

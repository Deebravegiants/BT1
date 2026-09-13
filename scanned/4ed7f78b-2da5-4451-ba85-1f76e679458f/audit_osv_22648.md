# [H] CVE-2022-3577

## Summary
Severity: High
Advisory: CVE-2022-3577
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-20
Source: https://osv.dev/vulnerability/CVE-2022-3577
Type: osv

## Details
An out-of-bounds memory write flaw was found in the Linux kernel’s Kid-friendly Wired Controller driver. This flaw allows a local user to crash or potentially escalate their privileges on the system. It is in bigben_probe of drivers/hid/hid-bigbenff.c. The reason is incorrect assumption - bigben devices all have inputs. However, malicious devices can break this assumption, leaking to out-of-bound write.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/gregkh/char-misc.git/commit/?h=char-misc-next&id=9d64d2405f7d30d49818f6682acd0392348f0fdb
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=945a9a8e448b65bec055d37eba58f711b39f66f0
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=fc4ef9d5724973193bfa5ebed181dba6de3a56db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3577.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3577

# [H] smb: client: fix krb5 mount with username option

## Summary
Severity: High
Advisory: CVE-2026-31392
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31392
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix krb5 mount with username option

Customer reported that some of their krb5 mounts were failing against
a single server as the client was trying to mount the shares with
wrong credentials.  It turned out the client was reusing SMB session
from first mount to try mounting the other shares, even though a
different username= option had been specified to the other mounts.

By using username mount option along with sec=krb5 to search for
principals from keytab is supported by cifs.upcall(8) since
cifs-utils-4.8.  So fix this by matching username mount option in
match_session() even with Kerberos.

For example, the second mount below should fail with -ENOKEY as there
is no 'foobar' principal in keytab (/etc/krb5.keytab).  The client
ends up reusing SMB session from first mount to perform the second
one, which is wrong.

```
$ ktutil
ktutil:  add_entry -password -p testuser -k 1 -e aes256-cts
Password for testuser@ZELDA.TEST:
ktutil:  write_kt /etc/krb5.keytab
ktutil:  quit
$ klist -ke
Keytab name: FILE:/etc/krb5.keytab
KVNO Principal
 ---- ----------------------------------------------------------------
   1 testuser@ZELDA.TEST (aes256-cts-hmac-sha1-96)
$ mount.cifs //w22-root2/scratch /mnt/1 -o sec=krb5,username=testuser
$ mount.cifs //w22-root2/scratch /mnt/2 -o sec=krb5,username=foobar
$ mount -t cifs | grep -Po 'username=\K\w+'
testuser
testuser
```

## References
- https://git.kernel.org/stable/c/12b4c5d98cd7ca46d5035a57bcd995df614c14e1
- https://git.kernel.org/stable/c/6e9ff1eb7feedcf46ff2d0503759960ab58e7775
- https://git.kernel.org/stable/c/9229709ec8bf85ae7ca53aeee9aa14814cdc1bd2
- https://git.kernel.org/stable/c/9ee803bfdba0cf739038dbdabdd4c02582c8f2b2
- https://git.kernel.org/stable/c/d33cbf0bf8979d779900da9be2505d68d9d8da25
- https://git.kernel.org/stable/c/fd4547830720647d4af02ee50f883c4b1cca06e4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git

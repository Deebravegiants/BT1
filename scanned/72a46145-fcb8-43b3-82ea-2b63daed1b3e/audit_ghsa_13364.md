# [H] copyparty vulnerable to path traversal attack

## Summary
Severity: High
Advisory: GHSA-pxfv-7rr3-2qjg
CVE: CVE-2023-37474
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-14
Source: https://github.com/advisories/GHSA-pxfv-7rr3-2qjg
Type: github-advisory

## Affected
- PyPI: `copyparty` — affected >=0 <1.8.2

## Details
# Summary
All versions before 1.8.2 have a path traversal vulnerability, allowing an attacker to download unintended files from the server.

# Details
Unauthenticated users were able to retrieve any files which are accessible (according to OS-level permissions) from the copyparty process. Usually, this is all files that are readable by the OS account which is used to run copyparty.

The vulnerability did not make it possible to list the contents of folders, so an attacker needs to know the full absolute path to the file, or the relative path from where copyparty is installed.

Some methods of running copyparty ([prisonparty](https://github.com/9001/copyparty/tree/hovudstraum/bin#prisonpartysh), the [nix package](https://github.com/9001/copyparty#nix-package), and [docker](https://github.com/9001/copyparty/tree/hovudstraum/scripts/docker)) had a mitigating effect, mostly reducing the attack scope to files inside copyparty volumes, and possibly the copyparty config file.

# Checking for attacks
Please keep in mind that, if an attacker were to find a way to overwrite the logs, for example by discovering the password to another service with sufficient privileges, then the following approaches cannot be trusted.

if copyparty was only accessible through a reverse proxy, then all attacks would be visible in the webserver access-log as URLs which contain both `.cpr/` and `%2F`
* nginx:
  ```bash
  (gzip -dc access.log*.gz; cat access.log) | sed -r 's/" [0-9]+ .*//' | grep -E 'cpr/.*%2[^0]' | grep -vF data:image/svg
  ```

However, if copyparty was directly accessible from the internet, then any successful attacks (file retrievals) would unfortunately leave no trace. That said, it is very probable that an attacker would make at least one invalid attempt, which would become apparent in the copyparty server log, detectable with `grep -aE '(Errno|Permission).*\.cpr/'` revealing the following:
* python2 example: `[IOError] [Errno 13] Permission denied: '/etc/shadow', .cpr//etc/shadow`
* python3 example: `[PermissionError] [Errno 13] Permission denied: b'/etc/shadow', .cpr//etc/shadow`
 

Providing an exact command for this approach is difficult, as it depends on how copyparty is deployed;
* if copyparty was running as a systemd service: `journalctl -am | grep -aE '(Errno|Permission).*\.cpr/'`
* if copyparty was logging to a compressed file: `xz -kdc thefilename.xz | grep -aE '(Errno|Permission).*\.cpr/'`
* if the copyparty log is available in a plaintext file: `grep -aE '(Errno|Permission).*\.cpr/' thefilename.txt`

# PoC / attack example
```bash
curl -sik http://127.0.0.1:3923/.cpr/%2Fetc%2Fpasswd
curl -sik http://127.0.0.1:3923/.cpr/..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd
```

## References
- https://github.com/9001/copyparty/security/advisories/GHSA-pxfv-7rr3-2qjg
- https://nvd.nist.gov/vuln/detail/CVE-2023-37474
- https://github.com/9001/copyparty/commit/043e3c7dd683113e2b1c15cacb9c8e68f76513ff
- https://github.com/9001/copyparty
- https://github.com/9001/copyparty/releases/tag/v1.8.2
- https://github.com/pypa/advisory-database/tree/main/vulns/copyparty/PYSEC-2023-127.yaml
- http://packetstormsecurity.com/files/173822/Copyparty-1.8.2-Directory-Traversal.html

# [H] Zoraxy has an authenticated command injection in the Web SSH feature

## Summary
Severity: High
Advisory: GHSA-7hpf-g48v-hw3j
CVE: CVE-2024-52010
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-7hpf-g48v-hw3j
Type: github-advisory

## Affected
- Go: `github.com/tobychui/zoraxy` — affected >=2.6.1 <3.1.3

## Details
### Summary
A command injection vulnerability in the Web SSH feature allows an authenticated attacker to execute arbitrary commands as root on the host.

### Details
Zoraxy has a Web SSH terminal feature that allows authenticated users to connect to SSH servers from their browsers.
In [`HandleCreateProxySession`](https://github.com/tobychui/zoraxy/blob/9cb315ea6739d1cc201b690322d25166b12dc5db/src/webssh.go#L19) the request to create an SSH session is handled. After checking for the presence of required parameters, ensuring that the target is not the loopback interface and that there is actually an SSH service running on the target, `CreateNewConnection` is called:

https://github.com/tobychui/zoraxy/blob/e79a70b7acfa45c2445aff9d60e4e7525c89fec8/src/mod/sshprox/sshprox.go#L165-L178

In line 178, the `gotty` binary is executed running `sshCommand` from the line above. It contains the user-controlled variable `connAddr`, which includes the hostname of the SSH server and - if provided - the username.
An attacker can exploit the `username` variable to escape from the `bash` command and inject arbitrary commands into `sshCommand`. This is possible, because, unlike hostname and port, the username is not validated or sanitized.

This vulnerability was introduced in https://github.com/tobychui/zoraxy/commit/c07d5f85dfc37bd32819358ed7d4bc32c604e8f0.
If Zoraxy is run without authentication of the management interface (started with`-noauth`), this vulnerability can be exploited without authentication.
Additionally, if Zoraxy is run in Docker with the Docker socket mounted (as described in https://github.com/tobychui/zoraxy/blob/9cb315ea6739d1cc201b690322d25166b12dc5db/docker/README.md), this vulnerability can be exploited to escape the Zoraxy container and gain access to the Docker host.

### PoC
1. Download and run Zoraxy as described in the [README](https://github.com/tobychui/zoraxy/blob/9a371f5bcbccce0918c61621f3b26ee549e01b90/README.md#standalone-mode)
2. Setup a user
3. Login as user
4. Navigate to Other -> Network Tools -> Connection
5. Enter hostname / IP of any server with SSH running, e.g. `github.com`
6. Enter `; bash ;` as user
7. Click `Connect using SSH`
8. A window will open with `bash` running on the Zoraxy host

Demo:

https://github.com/user-attachments/assets/5a3d8771-167f-4a79-8665-ed0dfb490181

### Impact
This vulnerability allows an authenticated attacker to gain remote code execution with the privileges of the Zoraxy process (root by default). This affects Zoraxy versions 2.6.1 through 3.1.2.

## References
- https://github.com/tobychui/zoraxy/security/advisories/GHSA-7hpf-g48v-hw3j
- https://nvd.nist.gov/vuln/detail/CVE-2024-52010
- https://github.com/tobychui/zoraxy/commit/2e9bc77a5d832bff1093058d42ce7a61382e4bc6
- https://github.com/tobychui/zoraxy/commit/c07d5f85dfc37bd32819358ed7d4bc32c604e8f0
- https://github.com/tobychui/zoraxy
- https://pkg.go.dev/vuln/GO-2024-3267

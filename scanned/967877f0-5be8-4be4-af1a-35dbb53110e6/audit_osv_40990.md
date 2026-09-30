# [H] Apache MINA SSHD: SSH certificate options lack validations

## Summary
Severity: High
Advisory: CVE-2026-56624
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-56624
Type: osv

## Details
Improper certificate validation in Apache MINA SSHD (server-side). Apache MINA SSHD is a Java library for client-side and server-side SSH.




Server-side OpenSSH user certificate validation during user authentication in an Apache MINA SSHD server did not check for the unsupported force-command or verify-required options that could be embedded in the certificate, nor did it validate these options. As a result it was possible that a user could authenticate with such a certificate that included a force-command option but still was able to execute other commands. What other command exactly would be available to the user depends on the implementation of the server.




This issue is fixed in Apache MINA SSHD 2.19.0 and 3.0.0-M5. Applications are advised to upgrade to these versions.




The fix rejects OpenSSH user certificates that include these options, since Apache MINA SSHD implements neither force-command nor sk-*-cert-v01@openssh.com user certificates (which are the only ones for which verify-required would make sense).

## References
- http://www.openwall.com/lists/oss-security/2026/07/20/17
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56624.json
- https://lists.apache.org/thread/o4c2jml522j3z80gbryqzc2f1253ltp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-56624

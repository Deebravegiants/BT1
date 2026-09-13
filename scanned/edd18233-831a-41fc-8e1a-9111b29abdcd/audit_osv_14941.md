# [H] CVE-2019-12499

## Summary
Severity: High
Advisory: CVE-2019-12499
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-31
Source: https://osv.dev/vulnerability/CVE-2019-12499
Type: osv

## Details
Firejail before 0.9.60 allows truncation (resizing to length 0) of the firejail binary on the host by running exploit code inside a firejail sandbox and having the sandbox terminated. To succeed, certain conditions need to be fulfilled: The jail (with the exploit code inside) needs to be started as root, and it also needs to be terminated as root from the host (either by stopping it ungracefully (e.g., SIGKILL), or by using the --shutdown control command). This is similar to CVE-2019-5736.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CDY7B73YDRBURA25APSHD5PFEO4TNSFW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RGVULJ6IKVDO6UAVIQRHQVSKOUD6QDWM/
- https://github.com/netblue30/firejail/issues/2401

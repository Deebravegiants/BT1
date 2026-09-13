# [M] ssl fails to validate incorrect extened key usage

## Summary
Severity: Medium
Advisory: CVE-2024-53846
Aliases: GHSA-qw6r-qh9v-638v
CVSS: 5.5 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2024-12-05
Source: https://osv.dev/vulnerability/CVE-2024-53846
Type: osv

## Details
OTP is a set of Erlang libraries, which consists of the Erlang runtime system, a number of ready-to-use components mainly written in Erlang, and a set of design principles for Erlang programs. A regression was introduced into the ssl application of OTP starting at OTP-25.3.2.8, OTP-26.2, and OTP-27.0, resulting in a server or client verifying the peer when incorrect extended key usage is presented (i.e., a server will verify a client if they have server auth ext key usage and vice versa).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53846.json
- https://github.com/erlang/otp/security/advisories/GHSA-qw6r-qh9v-638v
- https://nvd.nist.gov/vuln/detail/CVE-2024-53846

# [C] golang.org/x/crypto: FIDO/U2F security key physical presence check can be bypassed

## Summary
Severity: Critical
Advisory: GHSA-89gr-r52h-f8rx
CVE: CVE-2026-39831
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-89gr-r52h-f8rx
Type: github-advisory

## Affected
- Go: `golang.org/x/crypto` — affected >=0 <0.52.0

## Details
The Verify() method for FIDO/U2F security key types (sk-ecdsa-sha2-nistp256@openssh.com, sk-ssh-ed25519@openssh.com) did not check the User Presence flag. Signatures generated without physical touch were accepted, allowing unattended use of a hardware security key. To restore the previous behavior, return a "no-touch-required" extension in Permissions.Extensions from PublicKeyCallback.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-39831
- https://cs.opensource.google/go/x/crypto
- https://go.dev/cl/781662
- https://go.dev/issue/79566
- https://groups.google.com/g/golang-announce/c/a082jnz-LvI
- https://pkg.go.dev/vuln/GO-2026-5019

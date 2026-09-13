# [H] CVE-2018-15836

## Summary
Severity: High
Advisory: CVE-2018-15836
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-09-26
Source: https://osv.dev/vulnerability/CVE-2018-15836
Type: osv

## Details
In verify_signed_hash() in lib/liboswkeys/signatures.c in Openswan before 2.6.50.1, the RSA implementation does not verify the value of padding string during PKCS#1 v1.5 signature verification. Consequently, a remote attacker can forge signatures when small public exponents are being used. IKEv2 signature verification is affected when RAW RSA keys are used.

## References
- https://lists.openswan.org/pipermail/users/2018-August/023761.html
- https://github.com/xelerance/Openswan/commit/0b460be9e287fd335c8ce58129c67bf06065ef51
- https://github.com/xelerance/Openswan/commit/9eaa6c2a823c1d2b58913506a15f9474bf857a3d

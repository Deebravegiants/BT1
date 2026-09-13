# [M] CVE-2021-30004

## Summary
Severity: Medium
Advisory: CVE-2021-30004
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-04-02
Source: https://osv.dev/vulnerability/CVE-2021-30004
Type: osv

## Details
In wpa_supplicant and hostapd 2.9, forging attacks may occur because AlgorithmIdentifier parameters are mishandled in tls/pkcs1.c and tls/x509v3.c.

## References
- https://security.gentoo.org/glsa/202309-16
- https://w1.fi/cgit/hostap/commit/?id=a0541334a6394f8237a4393b7372693cd7e96f15

# [C] CVE-2022-37109

## Summary
Severity: Critical
Advisory: CVE-2022-37109
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-14
Source: https://osv.dev/vulnerability/CVE-2022-37109
Type: osv

## Details
patrickfuller camp up to and including commit bbd53a256ed70e79bd8758080936afbf6d738767 is vulnerable to Incorrect Access Control. Access to the password.txt file is not properly restricted as it is in the root directory served by StaticFileHandler and the Tornado rule to throw a 403 error when password.txt is accessed can be bypassed. Furthermore, it is not necessary to crack the password hash to authenticate with the application because the password hash is also used as the cookie secret, so an attacker can generate his own authentication cookie.

## References
- http://packetstormsecurity.com/files/171478/Raspberry-Pi-Camera-Server-1.0-Authentication-Bypass.html
- https://medium.com/%40elias.hohl/authentication-bypass-vulnerability-in-camp-a-raspberry-pi-camera-server-477e5d270904
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37109.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37109
- https://github.com/patrickfuller/camp/commit/bf6af5c2e5cf713e4050c11c52dd4c55e89880b1
- https://github.com/ehtec/camp-exploit

# [C] CVE-2021-27514

## Summary
Severity: Critical
Advisory: CVE-2021-27514
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/CVE-2021-27514
Type: osv

## Details
EyesOfNetwork 5.3-10 uses an integer of between 8 and 10 digits for the session ID, which might be leveraged for brute-force authentication bypass (such as in CVE-2021-27513 exploitation).

## References
- https://github.com/EyesOfNetworkCommunity/eonweb/issues/87
- https://github.com/ArianeBlow/exploit-eyesofnetwork5.3.10/blob/main/PoC-BruteForceID-arbitraty-file-upload-RCE-PrivEsc.py

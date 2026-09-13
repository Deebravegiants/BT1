# [H] CVE-2021-27513

## Summary
Severity: High
Advisory: CVE-2021-27513
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-22
Source: https://osv.dev/vulnerability/CVE-2021-27513
Type: osv

## Details
The module admin_ITSM in EyesOfNetwork 5.3-10 allows remote authenticated users to upload arbitrary .xml.php files because it relies on "le filtre userside."

## References
- https://github.com/EyesOfNetworkCommunity/eonweb/issues/87
- https://github.com/ArianeBlow/exploit-eyesofnetwork5.3.10/blob/main/PoC-BruteForceID-arbitraty-file-upload-RCE-PrivEsc.py

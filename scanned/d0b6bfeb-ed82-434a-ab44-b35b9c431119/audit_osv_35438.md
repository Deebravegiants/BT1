# [C] CVE-2025-8344

## Summary
Severity: Critical
Advisory: CVE-2025-8344
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-31
Source: https://osv.dev/vulnerability/CVE-2025-8344
Type: osv

## Details
A vulnerability classified as critical has been found in openviglet shio up to 0.3.8. Affected is the function shStaticFileUpload of the file shio-app/src/main/java/com/viglet/shio/api/staticfile/ShStaticFileAPI.java. The manipulation of the argument filename leads to unrestricted upload. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used.

## References
- https://vuldb.com/?id.318294
- https://vuldb.com/?submit.617680
- https://vuldb.com/?ctiid.318294
- https://github.com/openviglet/shio/issues/1029
- https://github.com/openviglet/shio/issues/1029#issue-3239422554

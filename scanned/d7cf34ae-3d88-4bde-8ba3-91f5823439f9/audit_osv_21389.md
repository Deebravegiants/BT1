# [C] CVE-2021-4261

## Summary
Severity: Critical
Advisory: CVE-2021-4261
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-19
Source: https://osv.dev/vulnerability/CVE-2021-4261
Type: osv

## Details
A vulnerability classified as critical has been found in pacman-canvas up to 1.0.5. Affected is the function addHighscore of the file data/db-handler.php. The manipulation leads to sql injection. It is possible to launch the attack remotely. Upgrading to version 1.0.6 is able to address this issue. The name of the patch is 29522c90ca1cebfce6453a5af5a45281d99b0646. It is recommended to upgrade the affected component. VDB-216270 is the identifier assigned to this vulnerability.

## References
- https://github.com/platzhersh/pacman-canvas/releases/tag/1.0.6
- https://vuldb.com/?id.216270
- https://github.com/platzhersh/pacman-canvas/commit/29522c90ca1cebfce6453a5af5a45281d99b0646

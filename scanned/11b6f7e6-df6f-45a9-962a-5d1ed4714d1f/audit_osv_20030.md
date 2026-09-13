# [H] CVE-2021-29466

## Summary
Severity: High
Advisory: CVE-2021-29466
Aliases: GHSA-p2pw-8xwf-879g
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-04-22
Source: https://osv.dev/vulnerability/CVE-2021-29466
Type: osv

## Details
Discord-Recon is a bot for the Discord chat service. In versions of Discord-Recon 0.0.3 and prior, a remote attacker is able to read local files from the server that can disclose important information. As a workaround, a bot maintainer can locate the file `app.py` and add `.replace('..', '')` into the `Path` variable inside of the `recon` function. The vulnerability is patched in version 0.0.4.

## References
- https://github.com/DEMON1A/Discord-Recon/security/advisories/GHSA-p2pw-8xwf-879g

# [H] CVE-2020-4044

## Summary
Severity: High
Advisory: CVE-2020-4044
Aliases: GHSA-j9fv-6fwf-p3g4
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-30
Source: https://osv.dev/vulnerability/CVE-2020-4044
Type: osv

## Details
The xrdp-sesman service before version 0.9.13.1 can be crashed by connecting over port 3350 and supplying a malicious payload. Once the xrdp-sesman process is dead, an unprivileged attacker on the server could then proceed to start their own imposter sesman service listening on port 3350. This will allow them to capture any user credentials that are submitted to XRDP and approve or reject arbitrary login credentials. For xorgxrdp sessions in particular, this allows an unauthorized user to hijack an existing session. This is a buffer overflow attack, so there may be a risk of arbitrary code execution as well.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00036.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00037.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00015.html
- https://github.com/neutrinolabs/xrdp/releases/tag/v0.9.13.1
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-j9fv-6fwf-p3g4
- https://www.debian.org/security/2020/dsa-4737
- https://github.com/neutrinolabs/xrdp/commit/0c791d073d0eb344ee7aaafd221513dc9226762c

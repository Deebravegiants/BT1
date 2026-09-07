# [H] Linuxfabrik Monitoring Plugins: Sudoers may be able to obtain privilege escalation via /usr/bin/apt-get arguments

## Summary
Severity: High
Advisory: GHSA-8w6w-23mq-h8rg
CVE: CVE-2026-52817
CWE: CWE-88
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-8w6w-23mq-h8rg
Type: github-advisory

## Affected
- PyPI: `linuxfabrik-lib` — affected >=0 <5.1.0

## Details
### Summary
In the [Debian.sudoers](https://github.com/Linuxfabrik/monitoring-plugins/blob/main/assets/sudoers/Debian.sudoers) file, `apt-get` is allowed for the nagios user. The full command including the arguments are not enforced and can therefore be choosen arbitrarily. This allows to easily get a root shell as the nagios user:

### PoC
By choosing a particular argument, you can get (as a nagios user) a root shell:
```
sudo apt-get update -o APT::Update::Pre-Invoke::="/bin/sh"
```
Since the nagious user can use sudo to run apt-get as root, the resulting shell is also running as root.

### Impact
The vulnerability is a local privilege escalation, impacting users who use the provided sudoers file. It requires that an attacker already compromised the nagios account (which is quite a high barrier to be honest).

### Fix
Since only one place where `apt-get` is currently used (in [deb-updates](https://github.com/Linuxfabrik/monitoring-plugins/blob/998302a5fb43e89df1359f4cbb6558f81c96ae4f/check-plugins/deb-updates/deb-updates#L124)) was found, it should be enough to allow only the specific arguments used there.

Here an example how the line in the sudoers file could look like:
```
                    /usr/lib64/nagios/plugins/strongswan-connections,\
                    /usr/lib64/nagios/plugins/systemd-unit,\
                    /usr/bin/apt-get update --quiet 2
```

## References
- https://github.com/Linuxfabrik/monitoring-plugins/security/advisories/GHSA-8w6w-23mq-h8rg
- https://github.com/Linuxfabrik/monitoring-plugins

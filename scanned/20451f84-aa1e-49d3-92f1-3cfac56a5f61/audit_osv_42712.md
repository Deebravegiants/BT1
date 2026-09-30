# [C] Dinky Unauthenticated Arbitrary File Write via /download/uploadFromRsByLocal Gated Only by Hardcoded Default Token

## Summary
Severity: Critical
Advisory: CVE-2026-70558
Aliases: GHSA-2p66-w3p3-5226
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-70558
Type: osv

## Details
Dinky's POST /download/uploadFromRsByLocal handler passes the caller-supplied path parameter directly to new File(path) and file.transferTo(dest) with no path validation. The route is marked @SaIgnore and /download/** is excluded from the Sa-Token interceptor, so the only guard is a header equality check against a dinkyToken value whose default (efda1551-7958-4e0f-80a8-dfd107df3e38) is hardcoded in source and shipped to every deployment. Anyone who can reach Dinky's HTTP port (8888 by default) and supplies the hardcoded token can write arbitrary files as the Dinky service account. The default Docker image runs on 8888 with no proxy or authentication and chmod 777 on /opt/dinky, so the application's own classpath, launch scripts, and static assets are writable. Demonstrated impact: overwriting /opt/dinky/config/static/index.html served attacker JavaScript to admin browsers immediately, and writing /opt/dinky/org/dinky/Dinky.class executed attacker code as the Dinky service account at the next JVM start via a classpath-shadow launched by script/bin/auto.sh. Writes are uid 9999 (flink), not root, so /etc, /root, /home, and /usr are refused. Affects Dinky v1.2.5 (the current release) and the development branch, where the code is byte-identical.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70558.json
- https://github.com/DataLinkDC/dinky/security/advisories/GHSA-2p66-w3p3-5226
- https://nvd.nist.gov/vuln/detail/CVE-2026-70558
- https://github.com/DataLinkDC/dinky
- https://github.com/DataLinkDC/dinky/issues/4566

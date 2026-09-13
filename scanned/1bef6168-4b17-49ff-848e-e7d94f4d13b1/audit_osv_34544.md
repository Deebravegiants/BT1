# [M] Traccar Unauthenticated Local File Inclusion on Windows - Leakage of Traccar Config File

## Summary
Severity: Medium
Advisory: CVE-2025-61666
Aliases: GHSA-hprc-rph8-fj87
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:N)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-61666
Type: osv

## Details
Traccar is an open source GPS tracking system. Default installs of Traccar on Windows between versions 6.1-  6.8.1 and non default installs between versions 5.8 - 6.0 are vulnerable to unauthenticated local file inclusion attacks which can lead to leakage of passwords or any file on the file system including the Traccar configuration file. Versions 5.8 - 6.0 are only vulnerable if <entry key='web.override'>./override</entry> is set in the configuration file. Versions 6.1 - 6.8.1 are vulnerable by default as the web override is enabled by default. The vulnerable code is removed in version 6.9.0.

## References
- https://github.com/traccar/traccar/blob/v6.8.1/src/main/java/org/traccar/web/DefaultOverrideServlet.java
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61666.json
- https://github.com/traccar/traccar/security/advisories/GHSA-hprc-rph8-fj87
- https://nvd.nist.gov/vuln/detail/CVE-2025-61666
- https://projectblack.io/blog/jetty-addpath-lfi

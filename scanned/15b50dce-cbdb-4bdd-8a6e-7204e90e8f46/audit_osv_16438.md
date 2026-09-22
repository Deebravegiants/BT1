# [H] CVE-2019-6962

## Summary
Severity: High
Advisory: CVE-2019-6962
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-20
Source: https://osv.dev/vulnerability/CVE-2019-6962
Type: osv

## Details
A shell injection issue in cosa_wifi_apis.c in the RDK RDKB-20181217-1 CcspWifiAgent module allows attackers with login credentials to execute arbitrary shell commands under the CcspWifiSsp process (running as root) if the platform was compiled with the ENABLE_FEATURE_MESHWIFI macro. The attack is conducted by changing the Wi-Fi network password to include crafted escape characters. This is related to the WebUI module.

## References
- https://dojo.bullguard.com/dojo-by-bullguard/blog/the-gateway-is-wide-open

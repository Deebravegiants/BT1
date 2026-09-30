# [H] CVE-2021-32287

## Summary
Severity: High
Advisory: CVE-2021-32287
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-09-20
Source: https://osv.dev/vulnerability/CVE-2021-32287
Type: osv

## Details
An issue was discovered in heif through v3.6.2. A global-buffer-overflow exists in the function HevcDecoderConfigurationRecord::getPicWidth() located in hevcdecoderconfigrecord.cpp. It allows an attacker to cause code Execution.

## References
- https://github.com/nokiatech/heif/issues/86

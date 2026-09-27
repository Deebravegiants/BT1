# [H] CVE-2019-1010239

## Summary
Severity: High
Advisory: CVE-2019-1010239
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-1010239
Type: osv

## Details
DaveGamble/cJSON cJSON 1.7.8 is affected by: Improper Check for Unusual or Exceptional Conditions. The impact is: Null dereference, so attack can cause denial of service. The component is: cJSON_GetObjectItemCaseSensitive() function. The attack vector is: crafted json file. The fixed version is: 1.7.9 and later.

## References
- https://github.com/DaveGamble/cJSON/issues/315
- https://github.com/DaveGamble/cJSON/commit/be749d7efa7c9021da746e685bd6dec79f9dd99b
- https://www.oracle.com/security-alerts/cpuoct2020.html

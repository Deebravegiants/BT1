# [H] can: denial-of-service can be triggered by a crafted CAN frame

## Summary
Severity: High
Advisory: CVE-2022-2741
Aliases: GHSA-hx5v-j59q-c3j8
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2022-10-31
Source: https://osv.dev/vulnerability/CVE-2022-2741
Type: osv

## Details
The denial-of-service can be triggered by transmitting a carefully crafted CAN frame on the same CAN network as the vulnerable node. The frame must have a CAN ID matching an installed filter in the vulnerable node (this can easily be guessed based on CAN traffic analyses). The frame must contain the opposite RTR bit as what the filter installed in the vulnerable node contains (if the filter matches RTR frames, the frame must be a data frame or vice versa).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2741.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-hx5v-j59q-c3j8
- https://nvd.nist.gov/vuln/detail/CVE-2022-2741

# [H] NULL-pointer dereference in UpdateHub OTA agent on empty inner metadata array (remote DoS)

## Summary
Severity: High
Advisory: CVE-2026-11810
Aliases: GHSA-jfpc-324j-84ww
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-11810
Type: osv

## Details
The UpdateHub firmware-update agent's probe handler (z_impl_updatehub_probe() in subsys/mgmt/updatehub/updatehub.c) parses the JSON metadata returned by the update server into a fixed two-level nested-array struct. After parsing it validates only the outer array length (objects_len != 2) and then dereferences objects[1].objects[0].objects.sha256sum via strlen() without checking that the inner object array of element [1] is non-empty.

The metadata is attacker-influenceable network input: the agent fetches it over CoAP from the configured UpdateHub server during its routine OTA probe. A malicious or compromised update server (or, when DTLS is disabled, a network man-in-the-middle) can return a response whose second outer object array is empty. Because the parse target is zero-initialised, the corresponding objects[1].objects[0].objects.sha256sum pointer is NULL, and the subsequent strlen() dereferences address zero. The same defect exists in both the 'any boards' and 'some boards' metadata layouts.

The resulting CPU fault is fatal under Zephyr's default error handling, halting or resetting the device, so the flaw is a remotely triggerable denial of service. Impact is limited to availability; it is a read from NULL with no out-of-bounds write, memory corruption, or information disclosure. The fix rejects metadata whose inner object array is empty before any dereference, on both layouts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11810.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-jfpc-324j-84ww
- https://nvd.nist.gov/vuln/detail/CVE-2026-11810
- https://github.com/zephyrproject-rtos/zephyr/commit/3424082022cb39d568434021b1d6f68b6a7fb3bf
- https://github.com/zephyrproject-rtos/zephyr

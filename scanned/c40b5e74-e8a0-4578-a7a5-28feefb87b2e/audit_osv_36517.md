# [M] EvseV2G has sequence state validation bypass

## Summary
Severity: Medium
Advisory: CVE-2026-24003
Aliases: GHSA-9vv5-67cv-9crq
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2026-24003
Type: osv

## Details
EVerest is an EV charging software stack. In versions up to and including 2025.12.1, it is possible to bypass the sequence state verification including authentication, and send requests that transition to forbidden states relative to the current one, thereby updating the current context with illegitimate data.cThanks to the modular design of EVerest, authorization is handled in a separate module and EVSEManager Charger internal state machine cannot transition out of the `WaitingForAuthentication` state through ISO 15118-2 communication. From this state, it was however possible through ISO 15118-2 messages which are published to the MQTT server to trick it into preparing to charge, and even to prepare to send current. The final requirement to actually send current to the EV was the closure of the contactors, which does not appear to be possible without leaving the `WaitingForAuthentication` state and leveraging ISO 15118-2 messages. As of time of publication, no fixed versions are available.

## References
- https://github.com/EVerest/everest-core/blob/main/modules/EVSE/EvseV2G/iso_server.cpp#L44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24003.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-9vv5-67cv-9crq
- https://nvd.nist.gov/vuln/detail/CVE-2026-24003

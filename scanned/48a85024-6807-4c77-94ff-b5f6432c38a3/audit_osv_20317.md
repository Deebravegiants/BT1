# [H] CVE-2021-32780

## Summary
Severity: High
Advisory: CVE-2021-32780
Aliases: BIT-envoy-2021-32780, GHSA-j374-mjrw-vvp8
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-24
Source: https://osv.dev/vulnerability/CVE-2021-32780
Type: osv

## Details
Envoy is an open source L7 proxy and communication bus designed for large modern service oriented architectures. In affected versions Envoy transitions a H/2 connection to the CLOSED state when it receives a GOAWAY frame without any streams outstanding. The connection state is transitioned to DRAINING when it receives a SETTING frame with the SETTINGS_MAX_CONCURRENT_STREAMS parameter set to 0. Receiving these two frames in the same I/O event results in abnormal termination of the Envoy process due to invalid state transition from CLOSED to DRAINING. A sequence of H/2 frames delivered by an untrusted upstream server will result in Denial of Service in the presence of untrusted **upstream** servers. Envoy versions 1.19.1, 1.18.4 contain fixes to stop processing of pending H/2 frames after connection transition to the CLOSED state.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-j374-mjrw-vvp8
- https://www.envoyproxy.io/docs/envoy/v1.19.0/version_history/version_history

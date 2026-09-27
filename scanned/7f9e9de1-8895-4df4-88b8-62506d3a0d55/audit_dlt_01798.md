# [?] Fix handleLCL consensus bug:

## Summary
Severity: Unknown
Chain: XRP
Component: XRPLF/rippled
Published: 2017-03-24
Source: https://github.com/XRPLF/rippled/commit/2449f9c18d8f4e9c0e864e809c977cb0fe0feca0
Type: security-commit

## Details
Fix handleLCL consensus bug:

Consensus::checkLCL can change state_ but it was being called inside
timerEntry after a switch on the current state_.  In rare cases, this might
end up calling stateEstablish even when the state_ was open.

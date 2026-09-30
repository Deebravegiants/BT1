# [M] unused returns

## Summary
Severity: Medium
Reporter: Delightful Felt Pangolin
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# unused returns

## Summary
unused return types on external function  in Locking/ GaugeController.vy
## Vulnerability Detail
@external
def checkpoint():
    """
    @notice Checkpoint to fill data common for all gauges.
    """
    self._get_total()


@external
def checkpoint_gauge(addr: address):
    """
    @notice Checkpoint to fill data for both a specific gauge and common for all gauges.
    @param addr Gauge address
    """
    self._get_weight(addr)
    self._get_total()

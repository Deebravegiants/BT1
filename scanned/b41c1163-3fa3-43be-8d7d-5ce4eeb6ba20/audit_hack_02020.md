# [M] 7.4 Reverting on setGaugeKilled()

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The AngleDistributor has the ability to remove the approval for a gauge through setGaugeKilled. That
function contains following line:


```
require(IGaugeController(controller).gauge_types(gaugeAddr)
== -1 && lastTimeGaugePaid[gaugeAddr] != 0, "112");
```
Note that the controller's gauge_types function is defined as follows:

```
gauge_type: int128 = self.gauge_types_[_addr]
assert gauge_type != 0
return gauge_type - 1
```
It reverts if the gauge type is 0 (return value -1). However, the first code snippet shows that the call
reverts if the return type is not -1. Hence, setGaugeKilled() will revert always revert.

Code corrected:

The precondition has been simplified to

```
require(lastTimeGaugePaid[gaugeAddr] != 0, "112");
```
Moreover, it can now only be called by guardians.

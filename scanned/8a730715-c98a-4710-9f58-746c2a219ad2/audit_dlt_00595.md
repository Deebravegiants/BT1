# [?] Fix race condition between validator duties service and proposer preferences (#9309)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2026-06-20
Source: https://github.com/sigp/lighthouse/commit/477c25db9f39bef5b3afb29643a257a8aa5d249b
Type: security-commit

## Details
Fix race condition between validator duties service and proposer preferences (#9309)

The proposer preferences service was attempting to publish preferences at the start of each epoch. This caused it to race with the validator duties service, it wouldn't calculate validator duties in time for the proposer preference service.

This PR first updates the validator duties service to calculate proposer duties for the current epoch and the next epoch. After Fulu we have the ability to look ahead one epoch for proposer duties, but we never updated the vc to leverage this feature.

This PR also updates the proposer preferences service to fire at every slot. We have an `(Epoch, DependentRoot)` map that prevents us from publishing the same preferences twice.

The changes here should prevent the race condition between the two services and make the proposer preferences service more robust in general.


  


Co-Authored-By: Eitan Seri- Levi <eserilev@gmail.com>

Co-Authored-By: Eitan Seri-Levi <eserilev@ucsc.edu>

Co-Authored-By: Michael Sproul <michaelsproul@users.noreply.github.com>

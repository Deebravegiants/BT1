# [M] 6.2 Dummy Iterations Can Be Avoided

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

The MinFirstAllocationStrategy features an algorithm which allocates items to buckets with different
capacities. In some cases, the algorithm may do many unnecessary dummy iterations, which each
allocate a single item to a bucket. For example:

```
1.Let's start with the scenario where we have 5 empty buckets, each with a very large capacity.
2.Now, call the allocate function, with an allocationSize of 24.
3.In the first five iterations, each bucket will be allocated 4 items, as 24 / 5 is rounded down to 4.
4.Now, an additional four "dummy" iterations have to be performed, which allocate an additional
single item to the first four buckets.
```
These dummy iterations could be avoided, for example, by rounding up instead of down when the
allocationSize is not divisible by the number of best candidates. This would result in the first four
iterations allocating 5 items each, with the last iteration having only four items left and allocating them all
to the last bucket.

Note that when a deposit occurs, this algorithm is run once for each staking module. Hence, as this
algorithm is executed many times, reducing the number of iterations could reduce business costs,
especially when more staking modules are added in the future.

Code corrected:

The allocation algorithm was updated. Now, when there are more than one best candidates, the ceil of
the division of the allocationSize by bestCandidatesCount is used.

```
allocated = Math256.min(
bestCandidatesCount > 1? Math256.ceilDiv(allocationSize, bestCandidatesCount) : allocationSize,
Math256.min(allocationSizeUpperBound, capacities[bestCandidateIndex]) - bestCandidateAllocation
);
```

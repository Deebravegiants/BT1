# [?] bug: fix algorithm overflow issues (#2173)

## Summary
Severity: Unknown
Chain: Fuel
Component: FuelLabs/fuel-core
Published: 2024-09-11
Source: https://github.com/FuelLabs/fuel-core/commit/f308bae9c9c784860b7d82ef0d71a695f862065e
Type: security-commit

## Details
bug: fix algorithm overflow issues (#2173)

## Linked Issues/PRs
Closes https://github.com/FuelLabs/fuel-core/issues/2164
Closes https://github.com/FuelLabs/fuel-core/issues/2147

## Description
The main change with this code is "normalizaing" the costs and rewards
instead of keeping a total over all time. i.e. every time we receive a
DA block, we see if the reward is greater than the costs, or vice versa.
If the reward is higher, we set the reward to the difference and set the
the last known cost to `0` and adjust the projected cost accordingly.

In addition, we were using a random set of types for the algorithm and
also used casts in many places. This PR should fix a lot of those
problems.

Bonus: This fix prompted me to run the optimization again. Since the set
is much bigger now, I decided to enable running the simulation in
parallel tasks to speed up the code.

## Checklist
- [x] New behavior is reflected in tests

### Before requesting review
- [x] I have reviewed the code myself

---------

Co-authored-by: green <xgreenx9999@gmail.com>
Co-authored-by: Aaryamann Challani <43716372+rymnc@users.noreply.github.com>

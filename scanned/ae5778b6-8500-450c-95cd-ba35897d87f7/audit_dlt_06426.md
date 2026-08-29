# [M] committee_sizes is not properly updated

## Summary
Severity: Medium
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-19
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/27
Type: hats-finding

## Details
**Github username:** @rodiontr
**Twitter username:** --
**Submission hash (on-chain):** 0x4b2b1181f80fffc7b9398573841ce7bc0d171de481009f1ef332f2ad124273b8
**Severity:** medium

**Description:**
**Description**\

`committee_sizes` variable is not updated when calling `set_committee()` function that may put the contract into an undesirable state as the variable is used for accounting purposes.


**Attack Scenario**\

In the `lib.rs`, there is a function called `set_committee()` that effectively can change the committee. However, the new length of the committee is not inserted into `committee_sizes` like it’s done in the `constructor()`:

https://github.com/Cardinal-Cryptography/most/blob/70ab234cc3322fda82784413f5e0704907a0e1fe/azero/contracts/most/lib.rs#L238-239
```
  let mut committee_sizes = Mapping::new();
            committee_sizes.insert(committee_id, &(committee.len() as u128));
```

And how it's done in the `set_committee()`:

```
self.ensure_owner()?;
            self.ensure_halted()?;
            Self::check_committee(&committee, signature_threshold)?;

            let mut data = self.data()?;

            let committee_id = data.committee_id + 1;
            let mut committee_set = Mapping::new();
            committee.into_iter().for_each(|account| {
                committee_set.insert((committee_id, account), &());
            });

            self.committees = committee_set;
            data.committee_id = committee_id;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/27_

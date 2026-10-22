# [M] Changing committee to a higher signature threshold will render a request from the previous committee un-processable

## Summary
Severity: Medium
Chain: Smart contract
Component: Most--Aleph-Zero-Bridge
Published: 2024-03-30
Source: https://github.com/hats-finance/Most--Aleph-Zero-Bridge-0xab7c1d45ae21e7133574746b2985c58e0ae2e61d/issues/63
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** @rnemes4
**Submission hash (on-chain):** 0x19c4ac85b9934ad8658ebdf55086e7b84773f7e023ba43c39f25fdb00a9fb99c
**Severity:** medium

**Description:**
## Title: 
Changing committee to a higher signature threshold will render a request from the previous committee un-processable

## Severity: 
Medium

## Description
The function `azero/contracts/most/lib.rs::receive_request` incorrectly uses the current committee signature threshold value as can be seen in the following snippet:

```Rust
let signature_threshold = self
                .signature_thresholds
                .get(data.committee_id) // @audit This shuld be using `committee_id` instead of `data.committee_id`?
                .ok_or(MostError::InvalidThreshold)?;
```

This means that a request from a previous committee with a lower threshold than the current would not be able to be processed if the committee members are changed and the threshold is increased.

### Scenario:
- An initial committee is setup with 4 members charlie, dave, eve and ferdie with a threshold of 4
- Alice creates a request 
- A new committee is created with 5 members charlie, dave, eve, mat and jenny with a threshold of 5
- Alices request is sent by charlie, dave, eve and ferdie, how ever the request will not get processed due to not meeting the current threshold of 5
- Alices request will be stuck and the funds she sent with will not be recoverable unless a new committee is created with exactly the same members and threshold as the original committee

## Recommendation
In order top fix this issue the following ammendment is recommended

```Rust
let signature_threshold = self
                .signature_thresholds
                .get(committee_id) // @audit This shuld be using `committee_id` instead of `data.committee_id`?
                .ok_or(MostError::InvalidThreshold)?;
```

ie: use the committee_id supplied in the request rather than the current committee Id

### Note
After checking the Solidity version, it was confirmed that the recommendation above is implemented correctly there.

## POC
Add the follwoing e2e test to `azero/contracts/tests/lib.rs`

```Rust
#[ink_e2e::test]
    fn can_process_previous_committee_requests_after_updating_committee_with higher_threshold(mut client: ink_e2e::Client<C, E>) {
        let (most_address, token_address) = setup_default_most_and_token(&mut client, true).await;

        most_set_halted(&mut client, &alice(), most_address, true)
            .await
            .expect("can set halted");

        most_set_committee(
            &mut client,
            &alice(),
            most_address,
            &guardian_ids()[1..],
            4, // Threshold
        )
        .await
        .expect("can set committee");

        most_set_halted(&mut client, &alice(), most_address, false)
        .await
        .expect("Set halt should succeed");

        let old_committee_id = 1;

        let amount = 841189100000000;

        let receiver_address = account_id(AccountKeyring::One);
        let request_nonce = 1;

        let request_hash = hash_request_data(
            old_committee_id,
            token_address,
            amount,
            receiver_address,
            request_nonce,
        );


        // Change Committee

        most_set_halted(&mut client, &alice(), most_address, true)
            .await
            .expect("can set halted");

        most_set_committee(
            &mut client,
            &alice(),
            most_address,
            &guardian_ids(),
            5, // Threshold,
        )
        .await
        .expect("can set committee");

        most_set_halted(&mut client, &alice(), most_address, false)
            .await
            .expect("can set halted");

        for i in 1..(guardian_ids().len() as usize) {
            let signer = &guardian_keys()[i];

            let receive_res = most_receive_request(
                &mut client,
                signer,
                most_address,
                request_hash,
                old_committee_id, // initial committee
                *token_address.as_ref(),
                amount,
                *receiver_address.as_ref(),
                request_nonce,
            )
            .await;

            match receive_res {
                Ok(call_res) => {
                    let events = call_res.events;
                    if i == ((guardian_ids().len() - 1) as usize) {
                        // @audit-info this is the last signature, so the request should be processed
                        assert_eq!(events.len(), 3); // Test fails here
                        assert_eq!(
                            filter_decode_events_as::<RequestProcessed>(vec![events[2].clone()])[0],
                            RequestProcessed {
                                request_hash,
                                dest_token_address: *token_address.as_ref(),
                            }
                        );
                    } else {
                        assert_eq!(events.len(), 1);
                        assert_eq!(filter_decode_events_as::<RequestSigned>(events).len(), 1);
                    }
                }
                Err(e) => panic!("Receive request should succeed: {:?}", e),
            }
        }
    }
```

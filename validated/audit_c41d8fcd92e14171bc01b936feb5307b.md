Looking at the external report's vulnerability class — **state updated before a potentially-failing operation, where failure leaves the state incorrect** — I need to find an analog in the NEAR MPC codebase.

Let me examine the `vote_reshared` flow and the `vote_tee_verifier_change` function carefully.
Looking at the external report's vulnerability class — **permanent asset freezing due to a recovery function that cannot rescue certain asset types** — I need to find an analog in the NEAR MPC codebase where funds or state become permanently unrecoverable due to a missing or overly-restrictive rescue path.

Let me examine the `propose_update` / `do_update` flow carefully.
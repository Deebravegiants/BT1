Looking at the external report's vulnerability class — **incorrect order of operations when updating a balance/pool, causing a value to be overcounted** — I need to find an analog in the Cardano Ledger codebase where a balance is updated with a value before a required deduction is applied to that value.

Let me examine the key accounting paths.
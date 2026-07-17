Looking at the external report's vulnerability class — **stale pending operations applied to a replaced entity** — I need to find an analog where an identifier is reused after the original entity is removed, and pending operations tied to that identifier execute against the new entity.

Let me trace the `remove_account` path and the `PromiseYield` lifecycle.
Looking at the bug class: **using a caller-supplied address as the "from" in a privileged operation without verifying the caller IS that address**. I need to find where the sequencer accepts a transaction on behalf of an address it has not authenticated.

Let me trace the gateway admission path carefully.